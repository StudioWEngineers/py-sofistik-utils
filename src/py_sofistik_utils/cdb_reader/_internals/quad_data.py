# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import DataFrame

# local library specific imports
from . group_data import Groups
from . sofistik_dll import SofDll
from . sofistik_classes import CQUAD


class QuadData:
    """This class provides methods and a data structure to:

        * access keys ``200/00`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``GROUP`` element group
        * ``ELEM_ID`` element number
        * ``N1`` id of the first node
        * ``N2``: id of the second node
        * ``N3``: id of the second node
        * ``N4``: id of the second node
        * ``MNO``: material number
        * ``NRA``: type of element

        The ``DataFrame`` uses a MultiIndex with level ``ELEM_ID`` to enable
        fast lookups via the `get` method. The index column is not dropped from
        the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * thickness
            * Jacobi Determinant
            * thickness
            * bedding factor
            * tangential bedding factor
            * transformation matrix
            * reinforcement material number

            are currently not included.

            This is a deliberate design choice and may be changed in the future
            without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "GROUP",
                "ELEM_ID",
                "N1",
                "N2",
                "N3",
                "N4",
                "MNO",
                "NRA"
            ]
        )
        self._dll = dll

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def get(
            self,
            element_id: int,
            quantity: str,
            default: float | int | None = None
    ) -> float | int:
        """Retrieve the requested quad quantity.

        Parameters
        ----------
        element_id : int
            Cable element number
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``"N1"``
            - ``"N2"``
            - ``"N3"``
            - ``"N4"``
            - ``"MNO"``
            - ``"NRA"``

        default : float or int or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float or int
            The requested quantity if found. Otherwise, returns ``default``
            when it is not None.

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
                f"Quad data entry not found for element id {element_id}, "
                f"and quantity {quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key
        ``200/00``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def load(self) -> None:
        """Retrieve all quad data. If the key does not exist or it is empty, a
        warning is raised only if ``echo_level > 0``.
        """
        if self._dll.key_exist(200, 0):
            quad = CQUAD()
            rec_length = c_int(sizeof(quad))
            return_value = c_int(0)

            data: list[dict[str, float | int]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    200,
                    0,
                    byref(quad),
                    byref(rec_length),
                    0 if first_call else 1
                )

                rec_length = c_int(sizeof(quad))
                first_call = False
                if return_value.value >= 2:
                    break

                data.append(
                    {
                        "GROUP":    0,
                        "ELEM_ID":  quad.m_nr,
                        "N1":       quad.m_node[0],
                        "N2":       quad.m_node[1],
                        "N3":       quad.m_node[2],
                        "N4":       quad.m_node[3],
                        "MNO":      quad.m_mat,
                        "NRA":      quad.m_nra
                    }
                )

            df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = df["ELEM_ID"]

            # assigning groups
            group_data = Groups(self._dll)
            group_data.load()

            for grp, grp_range in group_data.iterator("QUAD"):
                if grp_range.stop == 0:
                    continue
                left = elem_ids.searchsorted(grp_range.start, side="left")
                right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
                df.loc[df.index[left:right], "GROUP"] = grp

            # set indices for fast lookup and merge data
            self._data = df.set_index(["ELEM_ID"], drop=False)
