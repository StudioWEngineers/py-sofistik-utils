# standard library imports

# third party library imports
from pandas import DataFrame

# local library specific imports
from . beam_data import _BeamData
from . beam_results import BeamResults
from . beam_stresses import _BeamStress
from . sofistik_dll import SofDll


class Beam:
    """
    The ``Beam`` class is a wrapper that manages informations about beams
    through member variables of classes ``_BeamData``, ``_BeamResult`` and
    ``_BeamStresses``. It provides easy abstractions for commonly used data
    manipulations, e.g, calculating the strain energy or displacements in
    local coordinates.
    """

    data: _BeamData
    results: BeamResults
    stresses: _BeamStress

    def __init__(self, dll: SofDll) -> None:
        self.data = _BeamData(dll)
        self.results = BeamResults(dll)
        self.stresses = _BeamStress(dll)

        self._calculated_lc: set[int] = set()
        self._data = DataFrame(columns=["LOAD_CASE", "ID", "X", "Y", "Z"])
