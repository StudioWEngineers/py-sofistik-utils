# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any, Generator

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CGRP
from . sofistik_utilities import long_to_str


class _GroupData:
    """
    This class provides methods and data structure to:

    * access and load the key ``011/00`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_GroupData`` class.
        """
        self._dll = dll
        self._data: DataFrame = DataFrame(
            columns = [
                "GROUP",
                "GROUP_NAME",
                "BEAM_MIN_ID",
                "BEAM_MAX_ID",
                "NUMBER_OF_BEAMS",
                "TRUSS_MIN_ID",
                "TRUSS_MAX_ID",
                "NUMBER_OF_TRUSSES",
                "CABLE_MIN_ID",
                "CABLE_MAX_ID",
                "NUMBER_OF_CABLES",
                "SPRING_MIN_ID",
                "SPRING_MAX_ID",
                "NUMBER_OF_SPRINGS",
                "QUAD_MIN_ID",
                "QUAD_MAX_ID",
                "NUMBER_OF_QUADS"
            ]
        )

    def clear(self) -> None:
        """Clear all group data.
        """
        self._data = self._data[0:0]

    def get_beam_id_range(self, group_number: int) -> range:
        """Return a `range` starting from the minimum beam element ID to the maximum ID +
        1, so that a check like ``max_id in get_beam_id_range(grp_nmb)`` return `True`.

        If no beam elements are present in the given ``group_number`` return ``range(0)``.

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        if self._data.NUMBER_OF_BEAMS[mask].item() == 0:
            return range(0)

        max_id = self._data.BEAM_MAX_ID[mask].item()
        min_id = self._data.BEAM_MIN_ID[mask].item()

        return range(min_id, max_id + 1, 1)

    def get_cable_id_range(self, group_number: int) -> range:
        """Return a `range` starting from the minimum cable element ID to the maximum ID +
        1, so that a check like ``max_id in get_cable_id_range(grp_nmb)`` return `True`.

        If no cable elements are present in the given ``group_number`` return ``range(0)``.

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        if self._data.NUMBER_OF_CABLES[mask].item() == 0:
            return range(0)

        max_id = self._data.CABLE_MAX_ID[mask].item()
        min_id = self._data.CABLE_MIN_ID[mask].item()

        return range(min_id, max_id + 1, 1)

    def get_groups(self) -> list[int]:
        """Return a `list` of groups.
        """
        if self._data.GROUP.empty:
            raise RuntimeError("No groups found! Check if load() has been called.")

        return self._data.GROUP.to_list()

    def get_group_name(self, group_number: int) -> str:
        """Return a string containing the group name, given its number.

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        return str(self._data.GROUP_NAME[mask].item())

    def get_group_number(self, group_name: str) -> int:
        """Return the group number, given its name.

        Parameters
        ----------
        group_name: str
            The group name

        Raises
        ------
        RuntimeError
            If the given ``group_name`` is not found.
        """
        mask = self._data["GROUP_NAME"] == group_name.upper()

        if mask.eq(False).all():
            raise RuntimeError(f"Group \"{group_name}\" not found!")

        return int(self._data.GROUP[mask].item())

    def get_quad_id_range(self, group_number: int) -> range:
        """Return a `range` starting from the minimum quad element ID to the maximum ID
        + 1, so that a check like ``max_id in get_quad_id_range(grp_nmb)`` return `True`.

        If no quad elements are present in the given ``group_number`` return ``range(0)``.

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        if self._data.NUMBER_OF_QUADS[mask].item() == 0:
            return range(0)

        max_id = self._data.QUAD_MAX_ID[mask].item()
        min_id = self._data.QUAD_MIN_ID[mask].item()

        return range(min_id, max_id + 1, 1)

    def get_spring_id_range(self, group_number: int) -> range:
        """Return a `range` starting from the minimum spring element ID to the maximum ID
        + 1, so that a check like ``max_id in get_spring_id_range(grp_nmb)`` return `True`.

        If no spring elements are present in the given ``group_number`` return ``range(0)``
        .

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        if self._data.NUMBER_OF_SPRINGS[mask].item() == 0:
            return range(0)

        max_id = self._data.SPRING_MAX_ID[mask].item()
        min_id = self._data.SPRING_MIN_ID[mask].item()

        return range(min_id, max_id + 1, 1)

    def get_truss_id_range(self, group_number: int) -> range:
        """Return a `range` starting from the minimum truss element ID to the maximum ID
        + 1, so that a check like ``max_id in get_truss_id_range(grp_nmb)`` return `True`.

        If no truss elements are present in the given ``group_number`` return ``range(0)``.

        Parameters
        ----------
        group_number: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``group_number`` is not found.
        """
        mask = self._data["GROUP"] == group_number

        if mask.eq(False).all():
            raise RuntimeError(f"Group {group_number} not found!")

        if self._data.NUMBER_OF_TRUSSES[mask].item() == 0:
            return range(0)

        max_id = self._data.TRUSS_MAX_ID[mask].item()
        min_id = self._data.TRUSS_MIN_ID[mask].item()

        return range(min_id, max_id + 1, 1)

    def iterator_beam(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the beam ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_beam_id_range(grp))

    def iterator_cable(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the cable ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_cable_id_range(grp))

    def iterator_quad(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the quad ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_quad_id_range(grp))

    def iterator_spring(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the spring ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_spring_id_range(grp))

    def iterator_truss(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the truss ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_truss_id_range(grp))

    def load(self) -> None:
        """Load the group data.
        """
        if self._dll.key_exist(11, 0):
            g_data = CGRP()
            rec_length = c_int(sizeof(g_data))
            return_value = c_int(0)

            self.clear()

            temp_container: list[list[Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    11,
                    0,
                    byref(g_data),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                rec_length = c_int(sizeof(g_data))
                count += 1

                if return_value.value >= 2:
                    break

                temp_list: list[Any] = [0 for _ in range(17)]

                if g_data.m_typ == 0:
                    temp_list[0] = g_data.m_ng
                    g_name = "".join(long_to_str(g_data.m_text[_]) for _ in range(17))
                    temp_list[1] = g_name.upper()
                    temp_container.append(temp_list)

                else:
                    useful_data = True
                    match g_data.m_typ:
                        case 100:
                            type_index = 2
                        case 150:
                            type_index = 5
                        case 160:
                            type_index = 8
                        case 170:
                            type_index = 11
                        case 200:
                            type_index = 14
                        case _:
                            useful_data = False

                    if useful_data:
                        grp_index = [_[0] for _ in temp_container].index(g_data.m_ng)
                        temp_container[grp_index][type_index + 0] = g_data.m_min
                        temp_container[grp_index][type_index + 1] = g_data.m_max
                        temp_container[grp_index][type_index + 2] = g_data.m_num

            # preparing data for conversion to a pandas DataFrame
            conv_data: list[dict[str, Any]] = []
            for item in temp_container:
                conv_data.append({"GROUP":             item[0],
                                  "GROUP_NAME":        item[1],
                                  "BEAM_MIN_ID":       item[2],
                                  "BEAM_MAX_ID":       item[3],
                                  "NUMBER_OF_BEAMS":   item[4],
                                  "TRUSS_MIN_ID":      item[5],
                                  "TRUSS_MAX_ID":      item[6],
                                  "NUMBER_OF_TRUSSES": item[7],
                                  "CABLE_MIN_ID":      item[8],
                                  "CABLE_MAX_ID":      item[9],
                                  "NUMBER_OF_CABLES":  item[10],
                                  "SPRING_MIN_ID":     item[11],
                                  "SPRING_MAX_ID":     item[12],
                                  "NUMBER_OF_SPRINGS": item[13],
                                  "QUAD_MIN_ID":       item[14],
                                  "QUAD_MAX_ID":       item[15],
                                  "NUMBER_OF_QUADS":    item[16]})

            if self._data.empty:
                self._data = DataFrame(conv_data)
            else:
                self._data = concat(
                    [self._data, DataFrame(conv_data)],
                    ignore_index=True
                )
