# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_classes import CTRUS_RES
from . sofistik_dll import SofDll


class _TrussResult:
    """The ``_TrussResult`` class provides methods and data structure to:

    * access and load the keys ``152/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "AXIAL_FORCE",
                "AXIAL_DISPLACEMENT"
            ]
        )
        self._dll = dll
        self._echo_level = 0
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the results for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.loc[~(self._data["LOAD_CASE"] == load_case), :]
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear all group data.
        """
        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_element_force(self, element_number: int, load_case: int) -> float:
        """Return the cable connectivity for the given ``element_number``.

        Parameters
        ----------
        ``element_number``: int
            The cable element number
        ``load_case``: int
            The load case number

        Raises
        ------
        LookupError
            If the requested data is not found.
        """
        e_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (e_mask & lc_mask).eq(False).all():
            err_msg = f"LC {load_case}, EL_ID {element_number} not found!"
            raise LookupError(err_msg)

        return float(self._data.AXIAL_FORCE[e_mask & lc_mask].values[0])

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

        for grp, truss_range in group_data.iterator_truss():
            self._data.loc[self._data.ELEM_ID.isin(truss_range), "GROUP"] = grp

    def _load(self, load_case: int) -> list[dict[str, Any]]:
        """
        """
        trus = CTRUS_RES()
        record_length = c_int(sizeof(trus))
        return_value = c_int(0)

        data: list[dict[str, Any]] = []
        count = 0
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                152,
                load_case,
                byref(trus),
                byref(record_length),
                0 if count == 0 else 1
            )

            record_length = c_int(sizeof(trus))
            count += 1

            if return_value.value >= 2:
                break

            data.append(
                {
                    "LOAD_CASE":    load_case,
                    "GROUP":        0,
                    "ELEM_ID":      trus.m_nr,
                    "AXIAL_FORCE":  trus.m_n,
                    "AXIAL_DISP":   trus.m_v
                }
            )

        return data

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.
        """
        self._echo_level = echo_level
