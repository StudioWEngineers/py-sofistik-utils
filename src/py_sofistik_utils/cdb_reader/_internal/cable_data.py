# standard library imports
from ctypes import byref, c_int, sizeof

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
        """Retrieve all cable data. If the key is not found, a warning is raised only if
        ``echo_level > 0``.
        """
        if self._dll.key_exist(160, 0):
            cabl = CCABL()
            record_length = c_int(sizeof(cabl))
            return_value = c_int(0)

            self.clear()

            data: list[dict[str, float | int]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    160,
                    0,
                    byref(cabl),
                    byref(record_length),
                    0 if first_call else 1
                )

                record_length = c_int(sizeof(cabl))
                first_call = False
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

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            temp_df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = temp_df["ELEM_ID"]

            for grp, grp_range in group_data.iterator_cable():
                if grp_range.stop == 0:
                    continue

                left = elem_ids.searchsorted(grp_range.start, side="left")
                right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
                temp_df.loc[temp_df.index[left:right], "GROUP"] = grp

            # set indices for fast lookup
            temp_df = temp_df.set_index(["ELEM_ID"], drop=False)

            # merge data
            if self._data.empty:
                self._data = temp_df
            else:
                self._data = concat([self._data, temp_df])
