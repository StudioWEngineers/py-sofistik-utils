# standard library imports

# third party library imports

# local library specific imports
from . _internals.beam import Beam
from . _internals.cable import Cables
from . _internals.cross_section_data import CrossSectionalData
from . _internals.group_data import Groups
from . _internals.group_lc_data import GroupsLC
from . _internals.load_cases import LoadCases
from . _internals.node import Node
from . _internals.quad import Quads
from . _internals.sec_group_lc_data import SecondaryGroupsLC
from . _internals.spring import Spring
from . _internals.sofistik_dll import SofDll
from . _internals.truss import Truss


class SOFiSTiKCDBReader:
    """The ``SOFiSTiKCDBReader`` class provides efficient, read-only access to
    SOFiSTiK CDB files together with convenient data structures for fast
    querying, serialization, and interoperability with tools such as Pandas.
    """
    # elements
    beams: Beam
    cables: Cables
    nodes: Node
    quads: Quads
    springs: Spring
    trusses: Truss

    # other cdb data
    cross_sections: CrossSectionalData
    groups: Groups
    groups_lc: GroupsLC
    load_cases: LoadCases
    sec_groups_lc: SecondaryGroupsLC

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
        self.nodes = Node(self._dll)
        self.quads = Quads(self._dll)
        self.springs = Spring(self._dll)
        self.trusses = Truss(self._dll)

        # other cdb data
        self.cross_sections = CrossSectionalData(self._dll)
        self.groups = Groups(self._dll)
        self.groups_lc = GroupsLC(self._dll)
        self.load_cases = LoadCases(self._dll)
        self.sec_groups_lc = SecondaryGroupsLC(self._dll)

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
