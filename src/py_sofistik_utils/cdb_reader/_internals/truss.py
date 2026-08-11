# standard library imports

# third party library imports

# local library specific imports
from . truss_data import TrussData
from . truss_load import TrussLoad
from . truss_result import TrussResult
from . sofistik_dll import SofDll


class Truss:
    """
    High-level wrapper for truss-related data access and operations.

    The class aggregates the low-level interfaces ``_TrussData``,
    ``_TrussLoad``, and ``_TrussResults`` into a single abstraction. It
    provides a structured entry point for reading, manipulating and evaluating
    truss definitions, applied loads, and analysis results.
    """
    data: TrussData
    loads: TrussLoad
    results: TrussResult

    def __init__(self, dll: SofDll) -> None:
        self.data = TrussData(dll)
        self.loads = TrussLoad(dll)
        self.results = TrussResult(dll)
