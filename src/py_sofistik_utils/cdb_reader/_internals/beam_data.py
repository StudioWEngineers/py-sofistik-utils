# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CBEAM, CBEAM_SCT
from . sofistik_utilities import decode_beam_end_release


class _BeamData:
    """This class provides methods and a data structure to:

        * access keys ``100/00`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``GROUP``: group number
        * ``ELEM_ID``: beam number
        * ``N1``: start node
        * ``N2``: end node
        * ``LENGTH``: length
        * ``T_00``: transformation matrix
        * ``T_01``: transformation matrix
        * ``T_02``: transformation matrix
        * ``T_10``: transformation matrix
        * ``T_11``: transformation matrix
        * ``T_12``: transformation matrix
        * ``T_20``: transformation matrix
        * ``T_21``: transformation matrix
        * ``T_22``: transformation matrix
        * ``PROP_END_1``: property number at start
        * ``PROP_END_2``: property number at end
        * ``RELEASES_END_1``: end releases at start
        * ``RELEASES_END_2``: end releases at end

        The ``DataFrame`` uses a MultiIndex with level ``ELEM_ID`` to enable
        fast lookups via the `get` method. The index column is not dropped from
        the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * reference axis
            * distances along the reference axis
            * buckling length factors (YY and ZZ)
            * deformation length factors (YY and ZZ)
            * all remaining beam section information, other than end releases
              and cross section numbers

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
                "LENGTH",
                "T00",
                "T01",
                "T02",
                "T10",
                "T11",
                "T12",
                "T20",
                "T21",
                "T22",
                "PROP_END_1",
                "PROP_END_2",
                "RELEASES_END_1",
                "RELEASES_END_2"
            ]
        )
        self._dll = dll
        self._is_loaded = False

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]
        self._is_loaded = False

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key
        ``100/00``.

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
            quantity: str = "LENGTH",
            default: float | int | None = None
    ) -> float | int | str:
        """Retrieve the requested beam quantity.

        Parameters
        ----------
        element_id : int
            Beam element number
        quantity : str, default "LENGTH"
            Quantity to retrieve. Must be one of:

            - ``"N1"``
            - ``"N2"``
            - ``"LENGTH"``
            - ``"T00"``
            - ``"T01"``
            - ``"T02"``
            - ``"T10"``
            - ``"T11"``
            - ``"T12"``
            - ``"T20"``
            - ``"T21"``
            - ``"T22"``
            - ``"PROP_END_1"``
            - ``"PROP_END_2"``
            - ``"RELEASES_END_1"``
            - ``"RELEASES_END_2"``

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
                f"Beam data entry not found for element id {element_id}, "
                f"and quantity {quantity}!"
            ) from e

    def is_loaded(self) -> bool:
        """Return ``True`` if beam data have been loaded, ``False`` otherwise.
        """
        return self._is_loaded

    def load(self) -> None:
        """Retrieve all beam data. If the key does not exist or it is empty, a
        warning is raised only if ``echo_level > 0``.
        """
        if self._dll.key_exist(100, 0):
            beam = CBEAM()
            beam_sct = CBEAM_SCT()
            rec_length = c_int(sizeof(beam))
            rec_length_sct = c_int(sizeof(beam_sct))
            return_value = c_int(0)

            data_list: list[list[float | int | str]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    100,
                    0,
                    byref(beam),
                    byref(rec_length),
                    0 if first_call else 1
                )

                first_call = False
                if return_value.value >= 2:
                    break

                if beam.m_nr != 0:
                    data: list[float | int | str] = [0 for _ in range(18)]
                    data[0] = 0
                    data[1] = beam.m_nr
                    data[2] = beam.m_node[0]
                    data[3] = beam.m_node[1]
                    data[4] = beam.m_dl
                    data[5] = beam.m_t[0][0]
                    data[6] = beam.m_t[0][1]
                    data[7] = beam.m_t[0][2]
                    data[8] = beam.m_t[1][0]
                    data[9] = beam.m_t[1][1]
                    data[10] = beam.m_t[1][2]
                    data[11] = beam.m_t[2][0]
                    data[12] = beam.m_t[2][1]
                    data[13] = beam.m_t[2][2]
                    data_list.append(data)

                else:
                    self._dll.get(
                        1,
                        100,
                        0,
                        byref(beam_sct),
                        byref(rec_length_sct),
                        -1
                    )

                    # temporary workaround, here I assume that prop cannot be 0
                    if data_list[-1][14] == 0:
                        data_list[-1][14] = beam_sct.m_nq
                    else:
                        data_list[-1][15] = beam_sct.m_nq

                    if beam_sct.m_x == 0.:
                        data_list[-1][16] = decode_beam_end_release(
                            beam_sct.m_itp2
                        )
                    else:
                        data_list[-1][17] = decode_beam_end_release(
                            beam_sct.m_itp2
                        )
                    rec_length_sct = c_int(sizeof(beam_sct))

                rec_length = c_int(sizeof(beam))

            # preparing data for conversion to a pandas DataFrame
            conv_data: list[dict[str, float | int | str]] = []
            for item in data_list:
                conv_data.append(
                    {
                        "GROUP":          item[0],
                        "ELEM_ID":        item[1],
                        "N1":             item[2],
                        "N2":             item[3],
                        "LENGTH":         item[4],
                        "T00":            item[5],
                        "T01":            item[6],
                        "T02":            item[7],
                        "T10":            item[8],
                        "T11":            item[9],
                        "T12":            item[10],
                        "T20":            item[11],
                        "T21":            item[12],
                        "T22":            item[13],
                        "PROP_END_1":     item[14],
                        "PROP_END_2":     item[15],
                        "RELEASES_END_1": item[16],
                        "RELEASES_END_2": item[17]
                    }
                )

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            df = DataFrame(conv_data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = df["ELEM_ID"]

            for grp, grp_range in group_data.iterator_beam():
                if grp_range.stop == 0:
                    continue
                left = elem_ids.searchsorted(grp_range.start, side="left")
                right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
                df.loc[df.index[left:right], "GROUP"] = grp

            # set indices for fast lookup and override existing data, if any
            self._data = df.set_index(["ELEM_ID"], drop=False)
            self._is_loaded = True
