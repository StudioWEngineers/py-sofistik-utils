# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CTRUS


class _TrussData:
    """The ``_TrussData`` class provides methods and data structure to:

    * read-only access to the cdb file (only to the part related to the beam geometry);
    * store these information in a convenient format;
    * access these information.

    Beam data are stored in a :class:`pandas.DataFrame` with the following columns:

    * ``GROUP``: the beam group number
    * ``ELEM_ID``: the beam number
    * ``STATION``: :class:`numpy.ndarray` defining the position of the output stations
    * ``ADIMENSIONAL_STATION``: :class:`numpy.ndarray` defining the position of the output stations
      unitarized by the beam length
    * ``CONNECTIVITY``: :class:`numpy.ndarray` containing the start end nodes of the beam
    * ``TRANS_MATRIX``: the beam transformation matrix (3 x 3 :class:`numpy.ndarray`)
    * ``SPAR``: :class:`numpy.ndarray` with distances along a continuous beam or parameter values along
      the reference axis
    * ``PROPERTIES``: `list` containing the property number for each station

    """
    def __init__(self, dll: SofDll) -> None:
        self._data: DataFrame = DataFrame(
            columns = [
                "GROUP",
                "ELEM_ID",
                "N1",
                "N2",
                "L0",
                "PROPERTY",
                "GAP"
            ]
        )
        self._dll = dll

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key ``150/00``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the calling
            object's data and indices. Modifications to the data or indices of the
            copy will not be reflected in the original object (refer to
            :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def load(self) -> None:
        """Retrieve all truss data. If the key does not exist or it is empty, a warning is
        raised only if ``echo_level > 0``.
        """
        if self._dll.key_exist(150, 0):
            truss = CTRUS()
            record_length = c_int(sizeof(truss))
            return_value = c_int(0)

            self.clear()

            data: list[dict[str, float | int]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    150,
                    0,
                    byref(truss),
                    byref(record_length),
                    0 if first_call else 1
                )

                record_length = c_int(sizeof(truss))
                first_call = False
                if return_value.value >= 2:
                    break

                data.append(
                    {
                        "GROUP":    0,
                        "ELEM_ID":  truss.m_nr,
                        "N1":       truss.m_node[0],
                        "N2":       truss.m_node[1],
                        "L0":       truss.m_dl,
                        "PROPERTY": truss.m_nrq,
                        "GAP":      truss.m_gap
                    }
                )

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            temp_df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
            elem_ids = temp_df["ELEM_ID"]

            for grp, grp_range in group_data.iterator_truss():
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
