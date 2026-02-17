# standard library imports

# third party library imports

# local library specific imports
from . cable_data import _CableData
from . cable_load import _CableLoad
from . cable_result import _CableResult
from . sofistik_dll import SofDll


class _Cable:
    """
    High-level wrapper for cable-related data access and operations.

    The class aggregates the low-level interfaces ``_CableData``,
    ``_CableLoad``, and ``_CableResults`` into a single abstraction. It
    provides a structured entry point for reading, manipulating and evaluating
    cable definitions, applied loads, and analysis results.
    """
    data: _CableData
    load: _CableLoad
    result: _CableResult

    def __init__(self, dll: SofDll) -> None:
        self.data = _CableData(dll)
        self.load = _CableLoad(dll)
        self.result = _CableResult(dll)
