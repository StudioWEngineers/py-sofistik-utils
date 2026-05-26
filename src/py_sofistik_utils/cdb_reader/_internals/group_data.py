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
    """This class provides methods and a data structure to:

        * access keys ``11/0`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``GROUP"`` group number
        * ``GROUP_NAME"`` group nmae
        * ``BEAM_MIN_ID"`` beam minimum id
        * ``BEAM_MAX_ID"`` beam maximum id
        * ``NUMBER_OF_BEAMS"`` number of beams
        * ``TRUSS_MIN_ID"`` truss minimum id
        * ``TRUSS_MAX_ID"`` truss maximum id
        * ``NUMBER_OF_TRUSSES"`` number of trusses
        * ``CABLE_MIN_ID"`` cable minimum id
        * ``CABLE_MAX_ID"`` cable maximum id
        * ``NUMBER_OF_CABLES"`` number of cables
        * ``SPRING_MIN_ID"`` spring minimum id
        * ``SPRING_MAX_ID"`` spring maximum id
        * ``NUMBER_OF_SPRINGS"`` number of springs
        * ``QUAD_MIN_ID"`` quad minimum id
        * ``QUAD_MAX_ID"`` quad maximum id
        * ``NUMBER_OF_QUADS`` number of quads

        The ``DataFrame`` uses a MultiIndex with level ``GROUP``to enable fast
        lookups via the `get` method. The index columns are not dropped from
        the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * ``INF``: bit-code of the group
            * ``MNR``: material number of the group
            * ``MBW``: material reinforcement number of the group
            * ``IBB`` and ``IBD``: construction stage numbers

            are currently not included.

            This is a deliberate design choice and may be changed in the future
            without breaking the existing API.
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

    def get_id_range(self, quantity: str, group_number: int) -> range:
        """Return a `range` starting from the minimum element ID to the maximum
        ID + 1, so that a check like ``max_id in get_id_range("BEAM",
        group_number)`` returns `True`.

        If no elements of the requested type are present in the given
        ``group_number`` returns ``range(0)``.

        Parameters
        ----------
        quantity: str
            The type of finite element for which the range is requested. Must
            be one of:

            - ``"BEAM"``
            - ``"CABLE"``
            - ``"TRUSS"``
            - ``"SPRING"``
            - ``"QUAD"``

        group_number: int
            The group number
        """
        try:
            return range(
                self._data.at[group_number, f"{quantity}_MIN_ID"],  # type: ignore
                self._data.at[group_number, f"{quantity}_MAX_ID"] + 1  # type: ignore
            )
        except (KeyError, ValueError) as e:
            raise LookupError(
                f"Range not found for group number {group_number} "
                f"and quantity {quantity}!"
            ) from e

    def iterator_beam(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the beam ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_id_range("BEAM", grp))

    def iterator_cable(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the cable ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_id_range("CABLE", grp))

    def iterator_quad(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the quad ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_id_range("QUAD", grp))

    def iterator_spring(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the spring ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_id_range("SPRING", grp))

    def iterator_truss(self) -> Generator[tuple[int, range], None, None]:
        """Yield a tuple containing the group number and the truss ID range.
        """
        for grp in self.get_groups():
            yield (grp, self.get_id_range("TRUSS", grp))

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
