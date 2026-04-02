# standard library imports

# third party library imports
from pandas import DataFrame

# local library specific imports
from . beam_data import _BeamData
from . beam_load import _BeamLoad
from . beam_results import BeamResults
from . beam_stresses import _BeamStress
from . sofistik_dll import SofDll


class Beam:
    """
    The ``Beam`` class is a wrapper that manages informations about beams
    through member variables of classes ``_BeamData``, ``_BeamLoad``,
    ``_BeamResult`` and ``_BeamStresses``.
    It provides easy abstractions for commonly used data manipulations, e.g,
    calculating the strain energy.
    """

    data: _BeamData
    loads: _BeamLoad
    results: BeamResults
    stresses: _BeamStress

    def __init__(self, dll: SofDll) -> None:
        self.data = _BeamData(dll)
        self.loads = _BeamLoad(dll)
        self.results = BeamResults(dll)
        self.stresses = _BeamStress(dll)

        self._calculated_lc: set[int] = set()
        self._data = DataFrame(columns=["LOAD_CASE", "ID", "X", "Y", "Z"])
