# standard library imports

# third party library imports

# local library specific imports
from . _internals.beam import Beam
from . _internals.cable import Cables
from . _internals.cross_section_data import CrossSectionalData
from . _internals.group_data import _GroupData
from . _internals.group_lc_data import _GroupLCData
from . _internals.load_cases import _LoadCases
from . _internals.node import _Node
from . _internals.quad import Quads
from . _internals.sec_group_lc_data import _SecondaryGroupLCData
from . _internals.spring import _Spring
from . _internals.sofistik_dll import SofDll
from . _internals.truss import _Truss


class SOFiSTiKCDBReader:
    """The ``SOFiSTiKCDBReader`` class provides efficient, read-only access to
    SOFiSTiK CDB files together with convenient data structures for fast
    querying, serialization, and interoperability with tools such as Pandas.
    """
    # elements
    beams: Beam
    cables: Cables
    nodes: _Node
    quads: Quads
    springs: _Spring
    trusses: _Truss

    # other cdb data
    cross_sections: CrossSectionalData
    group_data: _GroupData
    group_lc_data: _GroupLCData
    load_cases: _LoadCases
    sec_group_lc_data: _SecondaryGroupLCData

    def __init__(
            self,
            path_to_cdb: str,
            file_name: str,
            path_to_dlls: str,
            version: int = 2023
    ) -> None:
        self._dll = SofDll(path_to_dlls, 0, version)
        self._echo_level = 0

        self.full_name = path_to_cdb + file_name + ".cdb"
        self.is_open = False

        # elements
        self.beams = Beam(self._dll)
        self.cables = Cables(self._dll)
        self.nodes = _Node(self._dll)
        self.quads = Quads(self._dll)
        self.springs = _Spring(self._dll)
        self.trusses = _Truss(self._dll)

        # other cdb data
        self.cross_sections = CrossSectionalData(self._dll)
        self.group_data = _GroupData(self._dll)
        self.group_lc_data = _GroupLCData(self._dll)
        self.load_cases = _LoadCases(self._dll)
        self.sec_group_lc_data = _SecondaryGroupLCData(self._dll)

    def close(self) -> None:
        """Close the CDB database.
        """
        self._dll.close()
        self.is_open = False

    def get_echo_level(self) -> int:
        """Return the ``echo_level`` of this instance of ``SOFiSTiKCDBReader``.
        """
        return self._echo_level

    def open(self) -> None:
        """Load the required SOFiSTiK dlls and open a CDB database in a
        read-only mode.
        """
        if not self.is_open:
            self._dll.initialize()
            self._dll.open_cdb(self.full_name)
            self.is_open = True

    def set_echo_level(self, new_echo_level: int) -> None:
        """Set the ``echo_level``.
        """
        self._echo_level = new_echo_level
        self._dll.set_echo_level(new_echo_level)
