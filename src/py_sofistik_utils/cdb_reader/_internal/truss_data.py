# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import DataFrame

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
        """The initializer of the `_`TrussData`` class.
        """
        self._data: DataFrame = DataFrame(
            columns = [
                "GROUP",
                "ELEM_ID",
                "PROPERTY",
                "N1",
                "N2",
                "L0",
                "PRE",
                "GAP"
            ]
        )
        self._dll = dll

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        self._data = self._data[0:0]

    def load(self) -> None:
        """Load truss data.
        """
        if self._dll.key_exist(150, 0):
            truss = CTRUS()
            rec_length = c_int(sizeof(truss))
            return_value = c_int(0)

            self.clear()

            temp_data: list[dict[str, Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    150,
                    0,
                    byref(truss),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                temp_data.append(
                    {
                        "GROUP":    0,
                        "ELEM_ID":  truss.m_nr,
                        "PROPERTY": truss.m_nrq,
                        "N1":       truss.m_node[0],
                        "N2":       truss.m_node[1],
                        "L0":       truss.m_dl,
                        "PRE":      truss.m_pre,
                        "GAP":      truss.m_gap
                    }
                )

                rec_length = c_int(sizeof(truss))
                count += 1

            self._data = DataFrame(temp_data)

            # assigning groups
            group_data = _GroupData(self._dll)
            group_data.load()

            for grp, truss_range in group_data.iterator_truss():
                self._data.loc[self._data.ELEM_ID.isin(truss_range), "GROUP"] = grp
