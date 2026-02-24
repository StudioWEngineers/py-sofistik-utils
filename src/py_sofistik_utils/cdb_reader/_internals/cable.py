# standard library imports

# third party library imports

# local library specific imports
from . cable_data import CableData
from . cable_load import CableLoad
from . cable_result import CableResult
from . sofistik_dll import SofDll


class Cables:
    """
    Façade aggregating cable-related components.

    The class aggregates the low-level interfaces ``CableData``,
    ``CableLoad`` and ``CableResults`` into a single abstraction. It
    provides a structured entry point for reading, manipulating and evaluating
    cable definitions, applied loads, and analysis results.
    """
    data: CableData
    load: CableLoad
    result: CableResult

    def __init__(self, dll: SofDll) -> None:
        self.data = CableData(dll)
        self.load = CableLoad(dll)
        self.result = CableResult(dll)
