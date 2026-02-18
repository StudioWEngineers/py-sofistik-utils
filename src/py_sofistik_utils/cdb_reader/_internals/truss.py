# standard library imports

# third party library imports

# local library specific imports
from . truss_data import _TrussData
from . truss_load import _TrussLoad
from . truss_result import _TrussResult
from . sofistik_dll import SofDll


class _Truss:
    """
    High-level wrapper for truss-related data access and operations.

    The class aggregates the low-level interfaces ``_TrussData``,
    ``_TrussLoad``, and ``_TrussResults`` into a single abstraction. It
    provides a structured entry point for reading, manipulating and evaluating
    truss definitions, applied loads, and analysis results.
    """
    data: _TrussData
    load: _TrussLoad
    result: _TrussResult

    def __init__(self, dll: SofDll) -> None:
        self.data = _TrussData(dll)
        self.load = _TrussLoad(dll)
        self.result = _TrussResult(dll)
