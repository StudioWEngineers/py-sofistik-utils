# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CCABL_RES


class _CableResults:
    """
    This class provides methods and data structure to:

    * access and load the keys ``162/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data: DataFrame = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "AXIAL_FORCE",
                "AVG_AXIAL_FORCE",
                "AXIAL_DISPLACEMENT",
                "RELAXED_LENGTH",
                "TOTAL_STRAIN",
                "EFFECTIVE_STIFFNESS"
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
        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve cable results for the given ``load_cases``. If a load case is not
        found, a warning is raised only if ``echo_level > 0``.

        Parameters
        ----------
        load_cases : int | list[int]
            load case numbers
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]

        # load data
        temp_list: list[dict[str, float | int | str]] = []
        for load_case in load_cases:
            if self._dll.key_exist(162, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        temp_df = DataFrame(temp_list).sort_values("ELEM_ID", kind="mergesort")
        elem_ids = temp_df["ELEM_ID"]

        for grp, grp_range in group_data.iterator_cable():
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

    def _load(self, load_case: int) -> list[dict[str, float | int | str]]:
        """Retrieve key ``162/load_case`` using SOFiSTiK dll.
        """
        cable_res = CCABL_RES()
        record_length = c_int(sizeof(cable_res))
        return_value = c_int(0)

        data: list[dict[str, float | int | str]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                162,
                load_case,
                byref(cable_res),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(cable_res))
            first_call = False
            if return_value.value >= 2:
                break

            if cable_res.m_nr > 0:
                data.append(
                    {
                        "LOAD_CASE": load_case,
                        "GROUP": 0,
                        "ELEM_ID": cable_res.m_nr,
                        "AXIAL_FORCE": cable_res.m_n,
                        "AVG_AXIAL_FORCE": cable_res.m_n_m,
                        "AXIAL_DISPLACEMENT": cable_res.m_v,
                        "RELAXED_LENGTH": cable_res.m_l0,
                        "TOTAL_STRAIN": cable_res.m_eps0,
                        "EFFECTIVE_STIFFNESS": cable_res.m_effs,
                    }
                )

        return data
