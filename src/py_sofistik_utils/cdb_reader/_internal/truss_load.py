# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

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

    def get_element_load(
            self,
            element_number: int,
            load_case: int,
            load_type: str
        ) -> Any:
        """Return the cable connectivity for the given ``element_number``.

        Parameters
        ----------
        ``element_number``: int
            The cable element number
        ``load_case``: int
            The load case number
        ``load_type``: str
            The load type

        Raises
        ------
        LookupError
            If the requested data is not found.
        """
        raise NotImplementedError
        e_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case
        lt_mask = self._data["TYPE"] == load_type

        if (e_mask & lc_mask & lt_mask).eq(False).all():
            err_msg = f"LC {load_case}, LT {load_type}, EL_ID {element_number} not found!"
            raise LookupError(err_msg)

        return self._data[e_mask & lc_mask & lt_mask].copy(deep=True)

    def load(self, load_cases: int | list[int]) -> None:
        """Load cable element loads for the given the ``load_cases``.

        If a load case is not found, a warning is raised only if ``echo_level`` is ``> 0``.

        Parameters
        ----------
        ``load_cases``: int | list[int], load case numbers
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]

        for load_case in load_cases:
            if self._dll.key_exist(151, load_case):
                self.clear(load_case)

                # load data
                data = DataFrame(self._load(load_case))

                # merge data
                if self._data.empty:
                    self._data = data
                else:
                    self._data = concat([self._data, data], ignore_index=True)
                self._loaded_lc.add(load_case)

            else:
                continue

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        for grp, cable_range in group_data.iterator_truss():
            self._data.loc[self._data.ELEM_ID.isin(cable_range), "GROUP"] = grp

    def _load(self, load_case: int) -> list[dict[str, Any]]:
        """
        """
        cabl = CTRUS_LOA()
        record_length = c_int(sizeof(cabl))
        return_value = c_int(0)

        data: list[dict[str, Any]] = []
        count = 0
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                151,
                load_case,
                byref(cabl),
                byref(record_length),
                0 if count == 0 else 1
            )

            record_length = c_int(sizeof(cabl))
            count += 1

            if return_value.value >= 2:
                break

            match cabl.m_typ:
                case 10:
                    type_ = "PG"
                case 11:
                    type_ = "PXX"
                case 12:
                    type_ = "PYY"
                case 13:
                    type_ = "PZZ"
                case 30:
                    type_ = "EX"
                case 31:
                    type_ = "WX"
                case 60:
                    type_ = "T"
                case 61:
                    type_ = "DT"
                case 70:
                    type_ = "VX"
                case 80:
                    type_ = "VX"
                case 111:
                    type_ = "PXP"
                case 212:
                    type_ = "PYP"
                case 313:
                    type_ = "PZP"
                case _:
                    raise RuntimeError(f"Unknown type: {cabl.m_typ}!")

            data.append(
                {
                    "LOAD_CASE":    load_case,
                    "GROUP":        0,
                    "ELEM_ID":      cabl.m_nr,
                    "TYPE":         type_,
                    "PA":           cabl.m_pa,
                    "PE":           cabl.m_pe,
                }
            )

        return data

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.
        """
        self._echo_level = echo_level
