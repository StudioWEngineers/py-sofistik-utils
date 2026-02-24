# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CCABL


class CableData:
    """This class provides methods and a data structure to:

        * access keys ``160/00`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``GROUP`` element group
        * ``ELEM_ID`` element number
        * ``N1`` id of the first node
        * ``N2``: id of the second node
        * ``L0``: initial length
        * ``PROPERTY``: property number (cross-section)

        The ``DataFrame`` uses a MultiIndex with level ``ELEM_ID`` to enable
        fast lookups via the `get` method. The index column is not dropped from
        the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * normal direction
            * prestress
            * element slip
            * maximum tension force
            * yielding load
            * reference axis

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
                "L0",
                "PROPERTY"
            ]
        )
        self._dll = dll
        self._echo_level = 0

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key
        ``160/00``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def get(
            self,
            element_id: int,
            quantity: str = "L0",
            default: float | int | None = None
    ) -> float | int:
        """Retrieve the requested cable quantity.

        Parameters
        ----------
        element_id : int
            Cable element number
        quantity : str, default "L0"
            Quantity to retrieve. Must be one of:

            - ``"N1"``
            - ``"N2"``
            - ``"L0"``
            - ``"PROPERTY"``

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
                f"Cable data entry not found for element id {element_id}, "
                f"and quantity {quantity}!"
            ) from e

    def load(self) -> None:
        """Retrieve all cable data. If the key does not exist or it is empty, a
        warning is raised only if ``echo_level > 0``.
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

            df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = df["ELEM_ID"]

            for grp, grp_range in group_data.iterator_cable():
                if grp_range.stop == 0:
                    continue

                left = elem_ids.searchsorted(grp_range.start, side="left")
                right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
                df.loc[df.index[left:right], "GROUP"] = grp

            # set indices for fast lookup
            df = df.set_index(["ELEM_ID"], drop=False)

            # merge data
            if self._data.empty:
                self._data = df
            else:
                self._data = concat([self._data, df])
