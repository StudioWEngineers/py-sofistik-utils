# standard library imports
from copy import deepcopy
from ctypes import byref, c_int, sizeof
from typing import Any, Generator

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_classes import CGRP_LC
from . sofistik_dll import SofDll
from . sofistik_utilities import long_to_str


class _SecondaryGroupLCData:
    """The ``_SecondaryGroupLCData`` class provides methods and data structure to:

    * access and load the key ``011/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.

    Only the secondary groups data are stored in this class.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_SecondaryGroupLCData`` class.
        """
        self._data: DataFrame = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
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
                "NUMBER_OF_QUADS",
                "IS_ACTIVE"
            ]
        )
        self._dll = dll
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the results for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.drop(self._data[self._data.LOAD_CASE == load_case].index)
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear all group data.
        """
        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_active_groups(self, load_case: int) -> list[str]:
        """For the given ``load_case``, return the list of active groups.

        Parameters
        ----------
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        active_mask = self._data["IS_ACTIVE"] == True

        return self._data.GROUP[lc_mask & active_mask].to_list()

    def get_beam_id_range(self, load_case: int, group_name: str) -> range:
        """For the given ``load_case``, return a range starting from the minimum beam
        element ID to the maximum ID + 1, so that a check like
        ``max_id in get_beam_id_range(lc, grp_nmb)`` return ``True``.

        If no beam elements are present in the given ``load_case`` and ``group_name``:
        return ``range(0)``.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            return range(0)

        max_id = self._data.BEAM_MAX_ID[lc_mask & grp_mask].item()
        min_id = self._data.BEAM_MIN_ID[lc_mask & grp_mask].item()

        return range(min_id, max_id + 1, 1)

    def get_cable_id_range(self, load_case: int, group_name: str) -> range:
        """For the given ``load_case``, return a range starting from the minimum cable
        element ID to the maximum ID + 1, so that a check like
        ``max_id in get_cable_id_range(lc, grp_nmb)`` return ``True``.

        If no cable elements are present in the given ``load_case`` and ``group_name``:
        return ``range(0)``.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            return range(0)

        max_id = self._data.CABLE_MAX_ID[lc_mask & grp_mask].item()
        min_id = self._data.CABLE_MIN_ID[lc_mask & grp_mask].item()

        return range(min_id, max_id + 1, 1)

    def get_quad_id_range(self, load_case: int, group_name: str) -> range:
        """For the given ``load_case``, return a `range` starting from the minimum quad
        element ID to the maximum ID + 1, so that a check like
        ``max_id in get_quad_id_range(lc, grp_nmb)`` return `True`.

        If no quad elements are present in the given ``load_case`` and ``group_name``:
        return ``range(0)``.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            return range(0)

        max_id = self._data.QUAD_MAX_ID[lc_mask & grp_mask].item()
        min_id = self._data.QUAD_MIN_ID[lc_mask & grp_mask].item()

        return range(min_id, max_id + 1, 1)

    def get_spring_id_range(self, load_case: int, group_name: str) -> range:
        """For the given ``load_case``, return a range starting from the minimum spring
        element ID to the maximum ID + 1, so that a check like
        ``max_id in get_spring_id_range(lc, grp_nmb)`` return ``True``.

        If no spring elements are present in the given ``load_case`` and ``group_name``:
        return ``range(0)``.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            return range(0)

        max_id = self._data.SPRING_MAX_ID[lc_mask & grp_mask].item()
        min_id = self._data.SPRING_MIN_ID[lc_mask & grp_mask].item()

        return range(min_id, max_id + 1, 1)

    def get_truss_id_range(self, load_case: int, group_name: str) -> range:
        """For the given ``load_case``, return a range starting from the minimum truss
        element ID to the maximum ID + 1, so that a check like
        ``max_id in get_truss_id_range(lc, grp_nmb)`` return ``True``.

        If no truss elements are present in the given ``load_case`` and ``group_name``:
        return ``range(0)``.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            return range(0)

        max_id = self._data.TRUSS_MAX_ID[lc_mask & grp_mask].item()
        min_id = self._data.TRUSS_MIN_ID[lc_mask & grp_mask].item()

        return range(min_id, max_id + 1, 1)

    def group_is_active(self, load_case: int, group_name: str) -> bool:
        """Return ``True`` if the given ``group_name:` is active` in the given ``load_case``.
        ``False`` otherwise.

        Parameters
        ----------
        group_name: str
            The group number
        load_case: int
            The load_case number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not loaded.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == group_name.upper()

        if (lc_mask & grp_mask).eq(False).all():
            err_msg = f"Group {group_name:} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return bool(self._data.IS_ACTIVE[lc_mask & grp_mask].item())

    def iterator_beam(self, load_case: int) -> Generator[tuple[str, range], None, None]:
        """Yield a tuple containing the group number and the beam ID range for the given
        ``load_case``.
        """
        for grp in self.get_active_groups(load_case):
            yield (grp, self.get_beam_id_range(load_case, grp))

    def iterator_cable(self, load_case: int) -> Generator[tuple[str, range], None, None]:
        """Yield a tuple containing the group number and the cable ID range for the given
        ``load_case``.
        """
        for grp in self.get_active_groups(load_case):
            yield (grp, self.get_cable_id_range(load_case, grp))

    def iterator_quad(self, load_case: int) -> Generator[tuple[str, range], None, None]:
        """Yield a tuple containing the group number and the quad ID range for the given
        ``load_case``.
        """
        for grp in self.get_active_groups(load_case):
            yield (grp, self.get_quad_id_range(load_case, grp))

    def iterator_spring(self, load_case: int) -> Generator[tuple[str, range], None, None]:
        """Yield a tuple containing the group number and the spring ID range for the given
        ``load_case``.
        """
        for grp in self.get_active_groups(load_case):
            yield (grp, self.get_spring_id_range(load_case, grp))

    def iterator_truss(self, load_case: int) -> Generator[tuple[str, range], None, None]:
        """Yield a tuple containing the group number and the truss ID range for the given
        ``load_case``.
        """
        for grp in self.get_active_groups(load_case):
            yield (grp, self.get_truss_id_range(load_case, grp))

    def load(self, load_case: int) -> None:
        """Load the group data for the given ``load_case``.
        """
        if self._dll.key_exist(11, load_case):
            g_data = CGRP_LC()
            rec_length = c_int(sizeof(g_data))
            return_value = c_int(0)

            self.clear(load_case)

            temp_container: list[list[Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    11,
                    load_case,
                    byref(g_data),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                rec_length = c_int(sizeof(g_data))
                count += 1

                if return_value.value >= 2:
                    break

                if g_data.m_ng <= 999:
                    continue

                temp_list: list[Any] = [0 for _ in range(18)]
                grp_name = long_to_str(g_data.m_ng)

                # dummy addition to avoid IndexError in the next if statement
                if not temp_container:
                    temp_container.append(deepcopy(temp_list))

                if grp_name != temp_container[-1][1]:
                    temp_list[0] = load_case
                    temp_list[1] = grp_name
                    temp_list[-1] = (2 & g_data.m_inf) > 0
                    temp_container.append(deepcopy(temp_list))

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
                        continue

                grp_index = [_[1] for _ in temp_container].index(grp_name)

                if (temp_container[grp_index][type_index + 0] == 0 or
                    g_data.m_min < temp_container[grp_index][type_index + 0]
                ):
                    temp_container[grp_index][type_index + 0] = g_data.m_min

                if g_data.m_max > temp_container[grp_index][type_index + 1]:
                    temp_container[grp_index][type_index + 1] = g_data.m_max

                temp_container[grp_index][type_index + 2] = g_data.m_num

            # manage case that there are no secondary group data for this load case
            if not temp_container:
                return

            # remove the dummy addition on line 400
            del temp_container[0]

            # preparing data for conversion to a pandas DataFrame
            conv_data: list[dict[str, Any]] = []
            for item in temp_container:
                conv_data.append({"LOAD_CASE":          item[0],
                                  "GROUP":              item[1],
                                  "BEAM_MIN_ID":        item[2],
                                  "BEAM_MAX_ID":        item[3],
                                  "NUMBER_OF_BEAMS":    item[4],
                                  "TRUSS_MIN_ID":       item[5],
                                  "TRUSS_MAX_ID":       item[6],
                                  "NUMBER_OF_TRUSSES":  item[7],
                                  "CABLE_MIN_ID":       item[8],
                                  "CABLE_MAX_ID":       item[9],
                                  "NUMBER_OF_CABLES":   item[10],
                                  "SPRING_MIN_ID":      item[11],
                                  "SPRING_MAX_ID":      item[12],
                                  "NUMBER_OF_SPRINGS":  item[13],
                                  "QUAD_MIN_ID":        item[14],
                                  "QUAD_MAX_ID":        item[15],
                                  "NUMBER_OF_QUADS":     item[16],
                                  "IS_ACTIVE":          item[17]})

            if self._data.empty:
                self._data = DataFrame(conv_data)
            else:
                self._data = concat(
                    [self._data, DataFrame(conv_data)],
                    ignore_index=True
                )
            self._loaded_lc.add(load_case)
