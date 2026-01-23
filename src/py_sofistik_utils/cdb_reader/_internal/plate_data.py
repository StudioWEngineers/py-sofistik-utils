"""
PlateData
---------

The `PlateData` class provides methods and data structure to:
    * read-only access to the cdb file (only to key 200/00);
    * store these information in a convenient format;
    * access these information.
"""
# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import DataFrame

# local library specific imports
from . group_data import GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CQUAD


class PlateData:
    """The `PlateData` class provides methods and data structure to:
    * read-only access to the cdb file (only to key 200/00);
    * store these information in a convenient format;
    * access these information.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `PlateData` class.
        """
        self._data: DataFrame = DataFrame(columns = ["GROUP",
                                                     "ELEM_ID",
                                                     "N1",
                                                     "N2",
                                                     "N3",
                                                     "N4",
                                                     "MNO",
                                                     "NRA"
                                                     ])
        self._dll = dll
        self._is_loaded = False

    def clear(self) -> None:
        """Clear the data set for all the quad elements.
        """
        self._data = self._data[0:0]
        self._is_loaded = False

    def load(self) -> None:
        """Load data set for all the quad elements.
        """
        if self._dll.key_exist(200, 0):
            quad = CQUAD()
            rec_length = c_int(sizeof(quad))
            return_value = c_int(0)

            self.clear()

            temp_container: list[list[int]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    200,
                    0,
                    byref(quad),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                if quad.m_nr != 0:
                    temp_list: list[int] = [0 for _ in range(8)]
                    temp_list[0] = 0
                    temp_list[1] = quad.m_nr
                    for i in range(0, 4):
                        temp_list[i + 2] = quad.m_node[i]
                    temp_list[6] = quad.m_mat
                    temp_list[7] = quad.m_nra

                    temp_container.append(temp_list)

                rec_length = c_int(sizeof(quad))
                count += 1

            # preparing data for conversion to a pandas DataFrame
            conv_data: list[dict[str, int]] = []
            for item in temp_container:
                conv_data.append({"GROUP"   : item[0],
                                  "ELEM_ID" : item[1],
                                  "N1"      : item[2],
                                  "N2"      : item[3],
                                  "N3"      : item[4],
                                  "N4"      : item[5],
                                  "MNO"     : item[6],
                                  "NRA"     : item[7],
                                  })

            self._data = DataFrame(conv_data)
            self._is_loaded = True

            # assigning groups
            group_data = GroupData(self._dll)
            group_data.load()

            for grp, quad_range in group_data.iterator_quad():
                self._data.loc[self._data.ELEM_ID.isin(quad_range), "GROUP"] = grp

    def get_connectivity(self) -> DataFrame:
        """Return the plate connectivity for all the plate elements.
        The first column represents the element IDs.
        """
        return self._data.iloc[:, 1:6].copy(deep=True)

    def get_element_connectivity(self, plate_nmb: int) -> DataFrame:
        """Return the plate connectivity for the given `plate_nmb`.
        The first value represents the element ID.

        Parameters
        ----------
        `plate_nmb`: int
            The plate number

        Raises
        ------
        RuntimeError
            If the given `plate_nmb` is not found.
        """
        mask = self._data["ELEM_ID"] == plate_nmb

        if mask.eq(False).all():
            raise RuntimeError(f"Element number {plate_nmb} not found!")

        return self._data.iloc[:, 1:6][mask].copy(deep=True)

    def get_group_connectivity(self, group_number: int|list[int]) -> DataFrame:
        """Return the plate connectivity for the given `grp_nmb`.
        The first column represents the element IDs.

        Parameters
        ----------
        `grp_nmb`: int | list[int]
            The plate group number

        Raises
        ------
        RuntimeError
            If the given `grp_nmb` is not found. In case a `list` of groups is passed, the
            error is raised of none of the groups is found.
        """
        if isinstance(group_number, int):
            grp_mask = self._data["GROUP"] == group_number
        else:
            grp_mask = self._data.GROUP.isin(group_number)

        if grp_mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        return self._data.iloc[:, 1:6][grp_mask].copy(deep=True)

    def get_material(self) -> DataFrame:
        """Return the plate material for all the plate elements.
        The first column represents the element IDs.
        """
        return self._data[["ELEM_ID", "MNO"]].copy(deep=True)

    def get_nra(self) -> DataFrame:
        """Return the plate NRA for all the plate elements.
        The first column represents the element IDs.
        """
        return self._data[["ELEM_ID", "NRA"]].copy(deep=True)

    def is_loaded(self) -> bool:
        """Return `True` if the plate data have been loaded from the cdb.
        """
        return self._is_loaded
