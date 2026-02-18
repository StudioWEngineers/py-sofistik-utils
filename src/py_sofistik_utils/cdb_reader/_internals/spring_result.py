# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CSPRI_RES


class _SpringResult:
    """This class provides methods and a data structure to:

        * access keys ``170/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``LOAD_CASE`` load case number
        * ``GROUP`` element group
        * ``ELEM_ID`` element number
        * ``FORCE`` axial force
        * ``TRANSVERSAL_FORCE``: transversal force
        * ``MOMENT``: axial moment
        * ``DISPLACEMENT``: axial displacement
        * ``TRANSVERSAL_DISPLACEMENT``: transversal displacement
        * ``ROTATION``: axial rotation

        The ``DataFrame`` uses a MultiIndex with levels ``ELEM_ID`` and
        ``LOAD_CASE`` (in this specific order) to enable fast lookups via the
        `get` method. The index columns are not dropped from the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * the three components along the global X, Y and Z axes for:
                - spring force
                - spring displacement
            * nonlinear effects
            * all quantities available if a workload has beed defined

            are currently not included. This is a deliberate design choice and
            may be changed in the future without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "FORCE",
                "TRANSVERSAL_FORCE",
                "MOMENT",
                "DISPLACEMENT",
                "TRANSVERSAL_DISPLACEMENT",
                "ROTATION"
            ]
        )
        self._dll = dll
        self._echo_level = 0
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
        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys
        ``170/LC``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def get(
            self,
            element_id: int,
            load_case: int,
            quantity: str = "FORCE",
            default: float | None = None
    ) -> float:
        """Retrieve the requested cable result.

        Parameters
        ----------
        element_id : int
            Cable element number
        load_case : int
            Load case number
        quantity : str, default "FORCE"
            Quantity to retrieve. Must be one of:

            - ``FORCE``
            - ``TRANSVERSAL_FORCE``
            - ``MOMENT``
            - ``DISPLACEMENT``
            - ``TRANSVERSAL_DISPLACEMENT``
            - ``ROTATION``

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
            return self._data.at[
                (element_id, load_case),
                quantity
            ]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Spring result entry not found for element id {element_id}, "
                f"load case {load_case}, and quantity {quantity}!"
            ) from e

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve spring results for the given ``load_cases``. If a load case
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
        temp_list: list[dict[str, float | int | str]] = []
        for load_case in load_cases:
            if self._dll.key_exist(170, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        temp_df = DataFrame(temp_list).sort_values("ELEM_ID", kind="mergesort")
        elem_ids = temp_df["ELEM_ID"]

        for grp, grp_range in group_data.iterator_spring():
            if grp_range.stop == 0:
                continue

            left = elem_ids.searchsorted(grp_range.start, side="left")
            right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
            temp_df.loc[temp_df.index[left:right], "GROUP"] = grp

        # set indices for fast lookup
        temp_df = temp_df.set_index(["ELEM_ID", "LOAD_CASE"], drop=False)

        # merge data
        if self._data.empty:
            self._data = temp_df
        else:
            self._data = concat([self._data, temp_df])
        self._loaded_lc.update(load_cases)

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.

        Parameters
        ----------
        echo_level : int
            the new echo level
        """
        self._echo_level = echo_level

    def _load(self, load_case: int) -> list[dict[str, float | int | str]]:
        """Retrieve key ``170/load_case`` using SOFiSTiK dll.
        """
        spri_res = CSPRI_RES()
        record_length = c_int(sizeof(spri_res))
        return_value = c_int(0)

        data: list[dict[str, float | int | str]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                170,
                load_case,
                byref(spri_res),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(spri_res))
            first_call = False
            if return_value.value >= 2:
                break

            if spri_res.m_nr > 0:
                data.append(
                    {
                        "LOAD_CASE": load_case,
                        "GROUP": 0,
                        "ELEM_ID": spri_res.m_nr,
                        "FORCE": spri_res.m_p,
                        "TRANSVERSAL_FORCE": spri_res.m_pt,
                        "MOMENT": spri_res.m_m,
                        "DISPLACEMENT": spri_res.m_v,
                        "TRANSVERSAL_DISPLACEMENT": spri_res.m_vt,
                        "ROTATION": spri_res.m_phi
                    }
                )

        return data
