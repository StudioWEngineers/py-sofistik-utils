# standard library imports

# third party library imports

# local library specific imports
from . quad_data import QuadData
from . sofistik_dll import SofDll


class Quads:
    """
    Façade aggregating quad-related components.

    Currently, this class only wraps the low-level interface ``QuadData``.
    It is nevertheless provided to maintain a consistent high-level API,
    similar to the interfaces used for ``Nodes``, ``Trusses``, ``Cables``, and
    other component classes.
    """
    data: QuadData

    def __init__(self, dll: SofDll) -> None:
        self.data = QuadData(dll)
