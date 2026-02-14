# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CSPRI


class _SpringData:
    """The ``_SpringData`` class provides methods and data structure to:

    * access and load the key ``170/00`` of the CDB file;
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
                "CP",
                "CT",
                "CM"
            ]
        )
        self._dll = dll
        self._echo_level = 0

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key ``170/00``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the calling
            object's data and indices. Modifications to the data or indices of the
            copy will not be reflected in the original object (refer to
            :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def get(
            self,
            element_id: int,
            quantity: str = "CP",
            default: float | int | None = None
        ) -> float | int:
        """Retrieve the requested spring quantity.

        Parameters
        ----------
        element_id : int
            Spring element number
        quantity : str, default "CP"
            Quantity to retrieve. Must be one of:

            - ``"N1"``
            - ``"N2"``
            - ``"CP"``
            - ``"CT"``
            - ``"CM"``

        default : float or int or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float or int
            The requested quantity if found. Otherwise, returns ``default`` when it is not
            None.

        Raises
        ------
        LookupError
            If the requested quantity is not found and ``default`` is None.
        """
        try:
            return self._data.at[element_id, quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Spring data entry not found for element id {element_id}, "
                f"and quantity {quantity}!"
            ) from e

    def load(self) -> None:
        """Retrieve all spring data. If the key does not exist or it is empty, a warning
        is raised only if ``echo_level > 0``.
        """
        if self._dll.key_exist(170, 0):
            spring = CSPRI()
            record_length = c_int(sizeof(spring))
            return_value = c_int(0)

            self.clear()

            data: list[dict[str, float | int]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    170,
                    0,
                    byref(spring),
                    byref(record_length),
                    0 if first_call else 1
                )

                record_length = c_int(sizeof(spring))
                first_call = False
                if return_value.value >= 2:
                    break

                data.append(
                    {
                        "GROUP":    0,
                        "ELEM_ID":  spring.m_nr,
                        "N1":       spring.m_node[0],
                        "N2":       spring.m_node[1],
                        "CP":       spring.m_cp,
                        "CT":       spring.m_cq,
                        "CM":       spring.m_cm
                    }
                )

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            temp_df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = temp_df["ELEM_ID"]

            for grp, grp_range in group_data.iterator_spring():
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

    def has_axial_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has an axial stiffness `!= 0`.

        Parameters
        ----------
        ``spring_nmb``: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given ``spring_nmb`` is not found.
        """
        return self.get_element_axial_stiffness(spring_nmb) != 0.0

    def has_lateral_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has a lateral stiffness `!= 0`.

        Parameters
        ----------
        ``spring_nmb``: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given ``spring_nmb`` is not found.
        """
        return self.get_element_lateral_stiffness(spring_nmb) != 0.0

    def has_rotational_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has a rotational stiffness != 0.

        Parameters
        ----------
        ``spring_nmb``: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given ``spring_nmb`` is not found.
        """
        return self.get_element_rotational_stiffness(spring_nmb) != 0.0
