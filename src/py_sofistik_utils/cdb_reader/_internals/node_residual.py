# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CN_DISPI


class _NodeResidual:
    """This class provides methods and a data structure to:

        * access keys ``170/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``LOAD_CASE``: load combination number
        * ``ID``: node number
        * ``UX``: X component of the nodal residual displacement (translation)
        * ``UY``: Y component of the nodal residual displacement (translation)
        * ``UZ``: Z component of the nodal residual displacement (translation)
        * ``URX``: X component of the nodal residual displacement (rotation)
        * ``URY``: Y component of the nodal residual displacement (rotation)
        * ``URZ``: Z component of the nodal residual displacement (rotation)
        * ``URB``: twist residual rotation
        * ``PX``: X component of the nodal residual reaction (translation)
        * ``PY``: Y component of the nodal residual reaction (translation)
        * ``PZ``: Z component of the nodal residual reaction (translation)
        * ``MX``: X component of the nodal residual reaction (rotation)
        * ``MY``: Y component of the nodal residual reaction (rotation)
        * ``MZ``: Z component of the nodal residual reaction (rotation)
        * ``MB``: warping residual moment

        The ``DataFrame`` uses a MultiIndex with levels ``ID`` and
        ``LOAD_CASE`` (in this specific order) to enable fast lookups via the
        `get` method. The index column is not dropped from the ``DataFrame``.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "ID",
                "UX",
                "UY",
                "UZ",
                "URX",
                "URY",
                "URZ",
                "URB",
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
            quantity: str,
            default: float | None = None
    ) -> float:
        """Retrieve the requested nodal result.

        Parameters
        ----------
        node_id : int
            Node number
        load_case : int
            Load case number
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``UX``
            - ``UY``
            - ``UZ``
            - ``URX``
            - ``URY``
            - ``URZ``
            - ``URB``
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

        Raises
        ------
        LookupError
            If the requested result is not found and ``default`` is None.
        """
        try:
            return self._data.at[(node_id, load_case), quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Node result entry not found for element id {node_id}, load "
                f"case {load_case}, and quantity {quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys
        ``26/LC``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve nodal results for the given ``load_cases``. If a load case
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
            if self._dll.key_exist(26, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # set indices for fast lookup
        temp_df = (
            DataFrame(temp_list)
            .set_index(["ID", "LOAD_CASE"], drop=False)
        )

        # merge data
        if self._data.empty:
            self._data = temp_df
        else:
            self._data = concat([self._data, temp_df])
        self._loaded_lc.update(load_cases)

    def _load(self, load_case: int) -> list[dict[str, float | int]]:
        """Retrieve key ``26/load_case`` using SOFiSTiK dll.
        """
        node = CN_DISPI()
        record_length = c_int(sizeof(node))
        return_value = c_int(0)

        self.clear(load_case)

        data: list[dict[str, float | int]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                26,
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
                        "UX": node.m_ux,
                        "UY": node.m_uy,
                        "UZ": node.m_uz,
                        "URX": node.m_urx,
                        "URY": node.m_ury,
                        "URZ": node.m_urz,
                        "URB": node.m_urb,
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
