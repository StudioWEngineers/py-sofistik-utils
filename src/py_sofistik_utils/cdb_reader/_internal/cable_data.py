# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CCABL


class _CableData:
    """
    This class provides methods and data structure to:

    * access and load the keys ``160/00`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data: DataFrame = DataFrame(
            columns = [
                "GROUP",
                "ELEM_ID",
                "N1",
                "N2",
                "L0",
                "PROPERTY"
            ]
        )
        self._dll = dll
        self._echo_level = 0

    def clear(self) -> None:
        """Clear all the cable element informations.
        """
        self._data = self._data[0:0]

    def get_element_connectivity(self, element_number: int) -> list[int]:
        """Return the cable connectivity for the given ``element_number``.

        Parameters
        ----------
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``element_number`` is not found.
        """
        raise NotImplementedError
        for group_data in self._connectivity.values():
            if element_number in group_data:
                return group_data[element_number]

        raise RuntimeError(f"Element number {element_number} not found!")

    def get_element_length(self, element_number: int) -> float:
        """Return the cable initial length for the given ``element_number``.

        Parameters
        ----------
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``element_number`` is not found.
        """
        raise NotImplementedError
        for group_data in self._initial_length.values():
            if element_number in group_data:
                return group_data[element_number]

        raise RuntimeError(f"Element number {element_number} not found!")

    def load(self) -> None:
        """Load cable element information given the group divisor number.

        Parameters
        ----------
        ``group_divisor``: int, optional default to 10000

        Raises
        ------
        RuntimeError
            If the key does not exist or it is empty.
        """
        if self._dll.key_exist(160, 0):
            cabl = CCABL()
            record_length = c_int(sizeof(cabl))
            return_value = c_int(0)

            self.clear()

            data: list[dict[str, Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    160,
                    0,
                    byref(cabl),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                data.append(
                    {
                        "GROUP":    0,
                        "ELEM_ID":  cabl.m_nr,
                        "N1":       cabl.m_node[0],
                        "N2":       cabl.m_node[1],
                        "L0":       cabl.m_dl,
                        "PROPERTY": cabl.m_nrq
                    }
                )

                record_length = c_int(sizeof(cabl))
                count += 1

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            data = DataFrame(data)
            for grp, cable_range in group_data.iterator_cable():
                data.loc[data.ELEM_ID.isin(cable_range), "GROUP"] = grp

            # merge data
            if self._data.empty:
                self._data = data
            else:
                self._data = concat([self._data, data], ignore_index=True)
