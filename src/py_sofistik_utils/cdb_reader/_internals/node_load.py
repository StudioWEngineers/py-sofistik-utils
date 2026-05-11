# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CNODE_L


class NodeLoad:
    """
    The ``NodeLoad`` class provides abstractions to load and access information
    about the nodal loads, contained in keys ``23/LC`` of the CDB file.

    Data are stored in a :class:`pandas.DataFrame` having the following
    columns:

    * ``LOAD_CASE``: load combination number
    * ``ID``: node number
    * ``PX``: X component of the nodal load (force, [kN])
    * ``PY``: Y component of the nodal load (force, [kN])
    * ``PZ``: Z component of the nodal load (force, [kN])
    * ``MX``: X component of the nodal load (moment, [kN/m])
    * ``MY``: Y component of the nodal load (moment, [kN/m])
    * ``MZ``: Z component of the nodal load (moment, [kN/m])
    * ``MB``: warping of the nodal load (moment, [kN/m])
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "ID",
                "PX",
                "PY",
                "PZ",
                "MX",
                "MY",
                "MZ",
                "MB"
            ]
        )
        self._dll = dll
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the loaded data for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data[
            self._data.index.get_level_values("LOAD_CASE") != load_case
        ]
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear the loaded data for all the load cases.
        """
        if not self._loaded_lc:
            return

        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get(
            self,
            node_id: int,
            load_case: int,
            quantity: str = "PZ",
            default: float | None = None
    ) -> float:
        """Retrieve the requested nodal load.

        Parameters
        ----------
        node_id : int
            Node number
        load_case : int
            Load case number
        quantity : str, default "PZ"
            Quantity to retrieve. Must be one of:

            - ``PX``
            - ``PY``
            - ``PZ``
            - ``MX``
            - ``MY``
            - ``MZ``
            - ``MB``

        default : float or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float
            The requested value if found. If not found, returns ``default``
            when it is not None.

        Notes
        -----
        If there are multiple entries for the same node and load case, this
        method returns the sum of all corresponding values. To access the
        individual entries without aggregation, use the `get_data` method.

        Raises
        ------
        LookupError
            If the requested load is not found and ``default`` is None.
        """
        value = self._data.loc[(node_id, load_case), quantity]
        try:
            return value if isinstance(value, (int, float)) else value.sum()  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Node load entry not found for element id {node_id}, load "
                f"case {load_case}, and quantity {quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys
        ``23/LC``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def is_loaded(self, load_case: int) -> bool:
        """Return `True` if the loads have been loaded for the given
        ``load_case``.
        """
        return load_case in self._loaded_lc

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve nodal loads for the given ``load_cases``. If a load case
        is not found, a warning is raised only if ``echo_level > 0``.

        Parameters
        ----------
        load_cases : int | list[int]
            load case numbers
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]
        else:
            load_cases = list(set(load_cases))  # remove duplicated entries

        # load data
        temp_list: list[dict[str, float | int]] = []
        for load_case in load_cases:
            if self._dll.key_exist(23, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # set indices for fast lookup
        temp_df = (
            DataFrame(temp_list)
            .set_index(["ID", "LOAD_CASE"], drop=False).sort_index()
        )

        # merge data
        if self._data.empty:
            self._data = temp_df
        else:
            self._data = concat([self._data, temp_df]).sort_index()
        self._loaded_lc.update(load_cases)

    def _load(self, load_case: int) -> list[dict[str, float | int]]:
        """Retrieve key ``23/load_case`` using SOFiSTiK dll.
        """
        node = CNODE_L()
        record_length = c_int(sizeof(node))
        return_value = c_int(0)

        self.clear(load_case)

        data: list[dict[str, float | int]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                23,
                load_case,
                byref(node),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(node))
            first_call = False
            if return_value.value >= 2:
                break

            if node.m_nr > 0:
                data.append(
                    {
                        "LOAD_CASE": load_case,
                        "ID": node.m_nr,
                        "PX": node.m_px,
                        "PY": node.m_py,
                        "PZ": node.m_pz,
                        "MX": node.m_mx,
                        "MY": node.m_my,
                        "MZ": node.m_mz,
                        "MB": node.m_mb
                    }
                )

        return data
