# standard library imports

# third party library imports

# local library specific imports
from . spring_data import _SpringData
from . spring_result import _SpringResult
from . sofistik_dll import SofDll


class _Spring:
    """
    High-level wrapper for spring-related data access and operations.

    The class aggregates the low-level interfaces ``_SpringData`` and
    ``_SpringResult`` into a single abstraction. It provides a structured entry
    point for reading, manipulating and evaluating truss definitions, applied
    loads, and analysis results.
    """
    data: _SpringData
    result: _SpringResult

    def __init__(self, dll: SofDll) -> None:
        self.data = _SpringData(dll)
        self.result = _SpringResult(dll)
