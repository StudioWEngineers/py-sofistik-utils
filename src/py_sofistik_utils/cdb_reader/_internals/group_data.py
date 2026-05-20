# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Generator

# third party library imports
from pandas import DataFrame

# local library specific imports
from . sofistik_classes import CGRP
from . sofistik_dll import SofDll
from . sofistik_utilities import long_to_str


class _GroupData:
    """
    This class provides methods and data structure to:

    * access and load the key ``011/00`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    _map = {
        100: ("BEAM_MIN_ID", "BEAM_MAX_ID", "NUMBER_OF_BEAMS"),
        150: ("TRUSS_MIN_ID", "TRUSS_MAX_ID", "NUMBER_OF_TRUSSES"),
        160: ("CABLE_MIN_ID", "CABLE_MAX_ID", "NUMBER_OF_CABLES"),
        170: ("SPRING_MIN_ID", "SPRING_MAX_ID", "NUMBER_OF_SPRINGS"),
        200: ("QUAD_MIN_ID", "QUAD_MAX_ID", "NUMBER_OF_QUADS"),
    }

    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
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
        self._dll = dll

    def clear(self) -> None:
        """Clear all the loaded data.
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

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key
        ``11/0``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

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
        """Load group data (key 11/0) from the CDB.
        """
        if self._dll.key_exist(11, 0):
            group = CGRP()
            rec_length = c_int(sizeof(group))
            return_value = c_int(0)

            data: dict[int, dict[str, float | int | str]] = {}
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    11,
                    0,
                    byref(group),
                    byref(rec_length),
                    0 if first_call else 1
                )

                rec_length = c_int(sizeof(group))
                first_call = False
                if return_value.value >= 2:
                    break

                if group.m_typ == 0:
                    name = "".join(
                        long_to_str(group.m_text[_]) for _ in range(17)
                    ).upper()
                    data.update(
                        {
                            group.m_ng: {
                                "GROUP":             group.m_ng,
                                "GROUP_NAME":        name,
                                "BEAM_MIN_ID":       0,
                                "BEAM_MAX_ID":       0,
                                "NUMBER_OF_BEAMS":   0,
                                "TRUSS_MIN_ID":      0,
                                "TRUSS_MAX_ID":      0,
                                "NUMBER_OF_TRUSSES": 0,
                                "CABLE_MIN_ID":      0,
                                "CABLE_MAX_ID":      0,
                                "NUMBER_OF_CABLES":  0,
                                "SPRING_MIN_ID":     0,
                                "SPRING_MAX_ID":     0,
                                "NUMBER_OF_SPRINGS": 0,
                                "QUAD_MIN_ID":       0,
                                "QUAD_MAX_ID":       0,
                                "NUMBER_OF_QUADS":   0
                            }
                        }
                    )

                else:
                    if group.m_typ in self._map.keys():
                        min_key, max_key, num_key = self._map[group.m_typ]
                        data[group.m_ng][min_key] = group.m_min
                        data[group.m_ng][max_key] = group.m_max
                        data[group.m_ng][num_key] = group.m_num

            # set indices for fast lookup
            self._data = (
                DataFrame(data.values()).set_index(["GROUP"], drop=False)
            )
