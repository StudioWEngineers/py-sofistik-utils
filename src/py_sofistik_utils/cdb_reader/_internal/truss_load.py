# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_classes import CTRUS_LOA
from . sofistik_dll import SofDll


class _TrussLoad:
    """The ``_TrussLoad`` class provides methods and data structure to:
    * access and load the keys ``161/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    _LOAD_TYPE_MAP = {
        10: "PG",
        11: "PXX",
        12: "PYY",
        13: "PZZ",
        30: "EX",
        31: "WX",
        60: "DT",
        61: "DT",
        70: "VX",
        80: "VX",
        111: "PXP",
        212: "PYP",
        313: "PZP"
    }

    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "TYPE",
                "PA",
                "PE"
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
        ``151/LC``.

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
            load_type: str,
            point: str = "PA",
            default: float | None = None
    ) -> float:
        """Retrieve the requested truss load.

        Parameters
        ----------
        element_id : int
            Truss element number
        load_case : int
            Load case number
        load_type : str
            Load type to retrieve. Must be one of:

            - ``"PG"``
            - ``"PXX"``
            - ``"PYY"``
            - ``"PZZ"``
            - ``"EX"``
            - ``"WX"``
            - ``"DT"``
            - ``"VX"``
            - ``"PXP"``
            - ``"PYP"``
            - ``"PZP"``

        point : str, default "PA"
            Location on the truss where the load is applied; either the start
            (``"PA"``) or the end (``"PE"``)
        default : float or None, default None
            Value to return if the requested load is not found

        Returns
        -------
        value : float
            The requested load if found. Otherwise, returns ``default`` when it
            is not None.

        Raises
        ------
        LookupError
            If the requested load is not found and ``default`` is None.
        """
        try:
            return self._data.at[
                (element_id, load_case, load_type), point
            ]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Truss load entry not found for element id {element_id}, load"
                f" case {load_case}, load type {load_type} and point {point}!"
            ) from e

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve truss load data for the given ``load_cases``. If a load
        case is not found, a warning is raised only if ``echo_level > 0``.

        Parameters
        ----------
        load_cases : int | list[int]
            load case numbers

        Notes
        -----
        Wind and snow loads are not implemented and will raise a runtime error
        if they are present in the requested load case.
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]
        else:
            load_cases = list(set(load_cases))  # remove duplicated entries

        # load data
        temp_list: list[dict[str, float | int | str]] = []
        for load_case in load_cases:
            if self._dll.key_exist(151, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        temp_df = DataFrame(temp_list).sort_values("ELEM_ID", kind="mergesort")
        elem_ids = temp_df["ELEM_ID"]

        for grp, grp_range in group_data.iterator_truss():
            if grp_range.stop == 0:
                continue

            left = elem_ids.searchsorted(grp_range.start, side="left")
            right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
            temp_df.loc[temp_df.index[left:right], "GROUP"] = grp

        # set indices for fast lookup
        temp_df = temp_df.set_index(
            ["ELEM_ID", "LOAD_CASE", "TYPE"],
            drop=False
        )

        # merge data
        if self._data.empty:
            self._data = temp_df
        else:
            self._data = concat([self._data, temp_df])
        self._loaded_lc.update(load_cases)

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.
        """
        self._echo_level = echo_level

    def _load(self, load_case: int) -> list[dict[str, float | int | str]]:
        """
        """
        trus = CTRUS_LOA()
        record_length = c_int(sizeof(trus))
        return_value = c_int(0)

        data: list[dict[str, float | int | str]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                151,
                load_case,
                byref(trus),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(trus))
            first_call = False
            if return_value.value >= 2:
                break

            try:
                type_ = _TrussLoad._LOAD_TYPE_MAP[trus.m_typ]
            except KeyError as e:
                raise RuntimeError(
                    f"Unknown truss load type {trus.m_typ} for element "
                    f"{trus.m_nr}!"
                ) from e

            data.append(
                {
                    "LOAD_CASE":    load_case,
                    "GROUP":        0,
                    "ELEM_ID":      trus.m_nr,
                    "TYPE":         type_,
                    "PA":           trus.m_pa,
                    "PE":           trus.m_pe,
                }
            )

        return data
