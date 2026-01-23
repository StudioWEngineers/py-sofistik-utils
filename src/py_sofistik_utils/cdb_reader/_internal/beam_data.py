"""
BeamData
--------

The `BeamData` class provides methods and data structure to:
    * read-only access to the cdb file (only to the part related to the beam geometry);
    * store these information in a convenient format;
    * access these information.

Beam data are stored in a `pd.DataFrame` with the following columns:
    * `GROUP`: the beam group number
    * `ELEM_ID`: the beam number
    * `STATION`: `np.array` defining the position of the output stations
    * `ADIMENSIONAL_STATION`: `np.array` defining the position of the output stations
unitarized by the beam length
    * `np.array[np.uint64]` containing the start end nodes of the beam
    * `TRANS_MATRIX`: the beam transformation matrix (3 x 3 `np.array`)
    * `SPAR`: `np.array` with distances along a continuous beam or parameter values along
the reference axis
    * `PROPERTIES`: `list` containing the property number for each station

"""
# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from numpy import array, float64, uint64
from numpy.typing import NDArray
from pandas import DataFrame, Series

# local library specific imports
from . group_data import GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CBEAM, CBEAM_SCT
from .sofistik_utilities import decode_beam_end_release


class BeamData:
    """The `BeamData` class provides methods and data structure to:
    * read-only access to the cdb file (only to the part related to the beam geometry);
    * store these information in a convenient format;
    * access these information.

    Beam data are stored in a `pd.DataFrame` with the following columns:
    * `GROUP`: the beam group number
    * `ELEM_ID`: the beam number
    * `STATION`: `np.array` defining the position of the output stations
    * `ADIMENSIONAL_STATION`: `np.array` defining the position of the output stations
unitarized by the beam length
    * `CONNECTIVITY`: `np.array[np.uint64]` containing the start end nodes of the beam
    * `TRANS_MATRIX`: the beam transformation matrix (3 x 3 `np.array`)
    * `SPAR`: `np.array` with distances along a continuous beam or parameter values along
the reference axis
    * `PROPERTIES`: `list` containing the property number for each station

    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `BeamData` class.
        """
        self._dll = dll

        self._data: DataFrame = DataFrame(columns = ["GROUP",
                                                     "ELEM_ID",
                                                     "STATION",
                                                     "ADIMENSIONAL_STATION",
                                                     "LENGTH",
                                                     "N1",
                                                     "N2",
                                                     "TRANS_MATRIX",
                                                     "SPAR",
                                                     "PROP_END_1",
                                                     "PROP_END_2",
                                                     "RELEASES_END_1",
                                                     "RELEASES_END_2"
                                                     ])

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def get_element_connectivity(self, element_number: int) -> NDArray[uint64]:
        """Return a shallow copy of the beam connectivity for the given `element_number`.

        Parameters
        ----------
        `element_number`: int
            The beam element number

        Raises
        ------
        RuntimeError
            If the given `element_number` is not found.
        """
        mask = self._data["ELEM_ID"] == element_number

        if mask.eq(False).all():
            raise RuntimeError(f"Element number {element_number} not found!")

        return self._data.CONNECTIVITY[mask].copy(deep = True).item()  # type: ignore

    def get_element_length(self, element_number: int) -> float:
        """Return a shallow copy of the beam length for the given `element_number`.

        Parameters
        ----------
        `element_number`: int
            The beam element number

        Raises
        ------
        RuntimeError
            If the given `element_number` is not found.
        """
        mask = self._data["ELEM_ID"] == element_number

        if mask.eq(False).all():
            raise RuntimeError(f"Element number {element_number} not found!")

        return self._data.LENGTH[mask].copy(deep = True).item()  # type: ignore

    def get_element_properties(self, element_number: int) -> list[int]:
        """Return a shallow copy of the beam properties for the given `element_number`.

        Parameters
        ----------
        `element_number`: int
            The beam element number

        Raises
        ------
        RuntimeError
            If the given `element_number` is not found.
        """
        mask = self._data["ELEM_ID"] == element_number

        if mask.eq(False).all():
            raise RuntimeError(f"Element number {element_number} not found!")

        return self._data.PROPERTIES[mask].to_list()[0]  # type: ignore

    def get_group_connectivity(self, group_number: int) -> "Series[type[object]]":
        """Return the beam connectivities for the given `grp_number`.

        Parameters
        ----------
        `group_number`: int
            The group number

        Raises
        ------
        RuntimeError
            If the given `grp_number` is not found.
        """
        grp_mask = self._data["GROUP"] == group_number

        if grp_mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        return self._data.CONNECTIVITY[grp_mask].copy(deep = True)

    def load(self) -> None:
        """Load beam data.
        """
        if self._dll.key_exist(100, 0):
            beam = CBEAM()
            beam_sct = CBEAM_SCT()
            rec_length = c_int(sizeof(beam))
            rec_length_sct = c_int(sizeof(beam_sct))
            return_value = 0

            self.clear()

            temp_container: list[list[Any]] = []
            count = 0
            while return_value < 2:
                return_value = self._dll.get(
                    1,
                    100,
                    0,
                    byref(beam),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                if return_value >= 2:
                    break

                if beam.m_nr != 0:
                    temp_list: list[Any] = [0 for _ in range(14)]
                    temp_list[1] = beam.m_nr
                    temp_list[2] = []
                    temp_list[4] = beam.m_dl
                    temp_list[5] = beam.m_node[0]
                    temp_list[6] = beam.m_node[1]
                    temp_list[7] = array(beam.m_t, dtype=float64)
                    temp_list[8] = array(beam.m_spar, dtype=float64)
                    temp_list[9] = 0
                    temp_list[10] = 0
                    temp_list[11] = ""
                    temp_list[12] = ""
                    temp_container.append(temp_list)

                else:
                    self._dll.get(
                        1,
                        100,
                        0,
                        byref(beam_sct),
                        byref(rec_length_sct),
                        -1
                    )
                    temp_container[-1][2].append(beam_sct.m_x)
                    # temporary workaround, here I assume that prop cannot be 0
                    if temp_container[-1][9] == 0:
                        temp_container[-1][9] = beam_sct.m_nq
                    else:
                        temp_container[-1][10] = beam_sct.m_nq

                    if beam_sct.m_x == 0.:
                        temp_container[-1][11] = decode_beam_end_release(beam_sct.m_itp2)
                    else:
                        temp_container[-1][12] = decode_beam_end_release(beam_sct.m_itp2)
                    rec_length_sct = c_int(sizeof(beam_sct))

                rec_length = c_int(sizeof(beam))
                count += 1

            # preparing data for conversion to a pandas DataFrame
            conv_data: list[dict[str, Any]] = []
            for item in temp_container:
                conv_data.append({"GROUP":                  item[0],
                                  "ELEM_ID":                item[1],
                                  "STATION":                array(item[2]),
                                  "ADIMENSIONAL_STATION":   item[3],
                                  "LENGTH":                 item[4],
                                  "N1":                     item[5],
                                  "N2":                     item[6],
                                  "TRANS_MATRIX":           item[7],
                                  "SPAR":                   item[8],
                                  "PROP_END_1":             item[9],
                                  "PROP_END_2":             item[10],
                                  "RELEASES_END_1":         item[11],
                                  "RELEASES_END_2":         item[12]
                                  })

            self._data = DataFrame(conv_data)

            # assigning groups
            group_data = GroupData(self._dll)
            group_data.load()

            for grp, beam_range in group_data.iterator_beam():
                self._data.loc[self._data.ELEM_ID.isin(beam_range), "GROUP"] = grp

            # calculating adimensional beam station X/L
            self._data.ADIMENSIONAL_STATION = self._data.STATION / self._data.LENGTH
