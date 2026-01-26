# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_lc_data import GroupLCData
from . sofistik_dll import SofDll
from . sofistik_classes import CBEAM_FOR


class _BeamResults:
    """The ``_BeamResults`` class provides methods and data structure to:

    * read-only access to the cdb file (only to the part related to the beam results);
    * store these results in a convenient format;
    * access these results

    Beam results are stored in a :class:`pandas.DataFrame` with the following columns:

    * ```load_case```: the load case number
    * ``GROUP``: the beam group number
    * ``ELEM_ID``: the beam number
    * ``STATION``: position of the output station along the beam
    * ``N``: axial force
    * ``VY``: shear force Y
    * ``VZ``: shear force Z
    * ``MT``: torsional moment
    * ``MY``: bending moment around Y
    * ``MZ``: bending moment around Z
    * ``MB``: warping moment
    * ``MT2``: second torsional moment
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_BeamResults`` class.
        """
        self._data: DataFrame = DataFrame(columns = ["LOAD_CASE",
                                                     "GROUP",
                                                     "ELEM_ID",
                                                     "STATION",
                                                     "N",
                                                     "VY",
                                                     "VZ",
                                                     "MT",
                                                     "MY",
                                                     "MZ",
                                                     "MB",
                                                     "MT2"])
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
        """Return a deep copy of all the beam results.
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
        if self._dll.key_exist(102, load_case):
            beam = CBEAM_FOR()
            record_length = c_int(sizeof(beam))
            return_value = 0

            self.clear(load_case)

            temp_container = []
            count = 0
            while return_value < 2:
                return_value = self._dll.get(
                    1,
                    102,
                    load_case,
                    byref(beam),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                if return_value >= 2:
                    break

                if beam.m_nr > 0:
                    temp_container.append({"LOAD_CASE": load_case,
                                           "GROUP": 0,
                                           "ELEM_ID": beam.m_nr,
                                           "STATION": beam.m_x,
                                           "N": beam.m_n,
                                           "VY": beam.m_vy,
                                           "VZ": beam.m_vz,
                                           "MT": beam.m_mt,
                                           "MY": beam.m_my,
                                           "MZ": beam.m_mz,
                                           "MB": beam.m_mb,
                                           "MT2": beam.m_mt2,
                                           })

                record_length = c_int(sizeof(beam))
                count += 1

            data = DataFrame(temp_container)

            # assigning groups
            group_lc_data = GroupLCData(self._dll)
            group_lc_data.load(load_case)

            for grp, beam_range in group_lc_data.iterator_beam(load_case):
                data.loc[data.ELEM_ID.isin(beam_range), "GROUP"] = grp

            if self._data.empty:
                self._data = data
            else:
                self._data = concat([self._data, data], ignore_index=True)
            self._loaded_lc.add(load_case)
