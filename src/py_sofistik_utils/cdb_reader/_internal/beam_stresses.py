# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_lc_data import _GroupLCData
from . sofistik_dll import SofDll
from . sofistik_classes import CBEAM_STR
from . sofistik_utilities import long_to_str


class _BeamStress:
    """
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_BeamStress`` class.
        """
        self._data: DataFrame = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "STATION",
                "SIG_C",
                "SIG_T",
                "TAU",
                "SIG_VM",
            ]
        )
        self._dll = dll
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the results for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.loc[~(self._data["LOAD_CASE"] == load_case), :]
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear all the results for all the load cases.
        """
        if not self._loaded_lc:
            return

        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_data(self) -> DataFrame:
        """Return a deep copy of all the beam_stress results.
        """
        return self._data.copy(deep = True)

    def load(self, load_case: int) -> None:
        """Load the results for the given ``load_case`` number.

        Parameters
        ----------
        load_case: int

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not found.
        """
        if self._dll.key_exist(105, load_case):
            beam_stress = CBEAM_STR()
            record_length = c_int(sizeof(beam_stress))
            return_value = c_int(0)

            self.clear(load_case)

            temp_container = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    105,
                    load_case,
                    byref(beam_stress),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                if beam_stress.m_nr > 0:
                    if (1024 & beam_stress.m_mnr) > 0 and beam_stress.m_mnr < 20000:
                        temp_container.append({
                            "LOAD_CASE": load_case,
                            "GROUP": 0,
                            "ELEM_ID": beam_stress.m_nr,
                            "STATION": beam_stress.m_x,
                            "SIG_C": beam_stress.m_sigc,
                            "SIG_T": beam_stress.m_sigt,
                            "TAU": beam_stress.m_tau,
                            "SIG_VM": beam_stress.m_sigv
                        })

                record_length = c_int(sizeof(beam_stress))
                count += 1

            data = DataFrame(temp_container)

            # assigning groups
            group_lc_data = _GroupLCData(self._dll)
            group_lc_data.load(load_case)

            for grp, beam_stress_range in group_lc_data.iterator_beam(load_case):
                data.loc[data.ELEM_ID.isin(beam_stress_range), "GROUP"] = grp

            if self._data.empty:
                self._data = data
            else:
                self._data = concat([self._data, data], ignore_index=True)
            self._loaded_lc.add(load_case)
