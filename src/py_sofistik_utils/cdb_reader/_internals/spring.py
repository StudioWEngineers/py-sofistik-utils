# standard library imports

# third party library imports

# local library specific imports
from . spring_data import SpringData
from . spring_result import SpringResult
from . sofistik_dll import SofDll


class Spring:
    """
    High-level wrapper for spring-related data access and operations.

    The class aggregates the low-level interfaces ``_SpringData`` and
    ``_SpringResult`` into a single abstraction. It provides a structured entry
    point for reading, manipulating and evaluating spring definitions, applied
    loads, and analysis results.
    """
    data: SpringData
    results: SpringResult

    def __init__(self, dll: SofDll) -> None:
        self.data = SpringData(dll)
        self.results = SpringResult(dll)
