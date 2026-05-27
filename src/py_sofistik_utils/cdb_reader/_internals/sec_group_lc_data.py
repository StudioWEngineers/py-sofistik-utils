# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_classes import CGRP_LC
from . sofistik_dll import SofDll
from . sofistik_utilities import long_to_str


class _SecondaryGroupLCData:
    """This class provides methods and a data structure to:

        * access secondary groups info in keys ``11/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``GROUP_NAME"`` group name
        * ``LOAD_CASE"`` the load case number
        * ``IS_ACTIVE"`` indicates whether the group is active in the load case

        The ``DataFrame`` uses a MultiIndex with level ``GROUP`` and
        ``LOAD_CASE`` (in this specific order) to enable fast lookups via the
        `is_active` method. The index columns are not dropped from the
        ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * ``MNR``: material number of the group
            * ``MBW``: material reinforcement number of the group
            * ``IBB`` and ``IBD``: construction stage numbers
            * ``MIN_ID``, ``MAX_ID`` and number of elements.

            are currently not included.

            This is a deliberate design choice and may be changed in the future
            without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "GROUP_NAME",
                "IS_ACTIVE"
            ]
        )
        self._dll = dll
        self._loaded_lc: set[int] = set()

    def active_groups(self, load_case: int) -> list[str]:
        """For the given ``load_case``, return the list of active secondary
        groups.

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
            raise RuntimeError(f"Load case {load_case} not loaded!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        active_mask = self._data["IS_ACTIVE"] is True

        return self._data.GROUP_NAME[lc_mask & active_mask].to_list()

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

    def is_active(self, group_name: str, load_case: int) -> bool:
        """Return `True` if the group ``group_name`` is active in the load case
        ``load_case``.
        """
        try:
            return self._data.at[(group_name, load_case), "IS_ACTIVE"]  # type: ignore
        except (KeyError, ValueError) as e:
            raise LookupError(
                f"Secondary group {group_name} not found in LC {load_case}!"
            ) from e

    def load(self, load_cases: int | list[bool | int]) -> None:
        """Retrieve group data for the given ``load_cases``.

        Parameters
        ----------
        load_cases : int | list[int]
            load case numbers
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]
        else:
            load_cases = list(set(load_cases))  # remove duplicated entries

        # load data
        data: list[dict[str, int]] = []
        for load_case in load_cases:
            if self._dll.key_exist(162, load_case):
                self.clear(load_case)
                data.extend(self._load(load_case))

        df = DataFrame(data).sort_values("GROUP_NAME", kind="mergesort")

        # set indices for fast lookup
        df = df.set_index(["GROUP_NAME", "LOAD_CASE"], drop=False)

        # merge data
        if self._data.empty:
            self._data = df
        else:
            self._data = concat([self._data, df])
        self._loaded_lc.update(load_cases)

    def _load(self, load_case: int) -> list[dict[str, bool | int]]:
        """Load secondary groups info in key ``11/load_case`` from the CDB.
        """
        group = CGRP_LC()
        rec_length = c_int(sizeof(group))
        return_value = c_int(0)

        data: dict[int, dict[str, bool | int]] = {}
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                11,
                load_case,
                byref(group),
                byref(rec_length),
                0 if first_call else 1
            )

            rec_length = c_int(sizeof(group))
            first_call = False
            if return_value.value >= 2:
                break

            if group.m_ng <= 999:
                continue

            data.update(
                {
                    group.m_ng: {
                        "GROUP_NAME": long_to_str(group.m_ng),
                        "LOAD_CASE":  load_case,
                        "IS_ACTIVE":  bool(group.m_inf & 2)
                    }
                }
            )

        return list(data.values())
