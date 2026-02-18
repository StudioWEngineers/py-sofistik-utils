"""
SOFiSTiKCDBReader
-----------------

The ``SOFiSTiKCDBReader`` class provides methods and data structure to read-only access to a
SOFiSTiK cdb file and serialize its content.
"""
# standard library imports

# third party library imports

# local library specific imports
from . _internals.beam_data import _BeamData
from . _internals.beam_load import _BeamLoad
from . _internals.beam_results import _BeamResults
from . _internals.beam_stresses import _BeamStress
from . _internals.cable import _Cable
from . _internals.group_data import _GroupData
from . _internals.group_lc_data import _GroupLCData
from . _internals.load_cases import _LoadCases
from . _internals.nodes import _Nodes
from . _internals.plate_data import _PlateData
from . _internals.property import _PropertyData
from . _internals.sec_group_lc_data import _SecondaryGroupLCData
from . _internals.spring import _Spring
from . _internals.sofistik_dll import SofDll
from . _internals.truss import _Truss


class SOFiSTiKCDBReader:
    """The ``SOFiSTiKCDBReader`` class provides methods and data structure to read-only
    access to a SOFiSTiK cdb file and serialize its content.
    """
    beam_geo: _BeamData
    beam_load: _BeamLoad
    beam_res: _BeamResults
    cable: _Cable
    beam_stress: _BeamStress
    grp_data: _GroupData
    grp_lc_data: _GroupLCData
    load_case: _LoadCases
    nodes: _Nodes
    plate_data: _PlateData
    properties: _PropertyData
    sec_grp_lc_data: _SecondaryGroupLCData
    spring: _Spring
    truss: _Truss

    def __init__(
            self,
            path_to_cdb: str,
            file_name: str,
            path_to_dlls: str,
            version: int = 2023
    ) -> None:
        """The initializer of the ``SOFiSTiKCDBReader`` class.
        """
        self._echo_level = 0
        self.full_name = path_to_cdb + file_name + ".cdb"
        self.is_open = False

        self._dll = SofDll(path_to_dlls, self.get_echo_level(), version)

        self.beam_res = _BeamResults(self._dll)
        self.beam_geo = _BeamData(self._dll)
        self.beam_load = _BeamLoad(self._dll)
        self.beam_stress = _BeamStress(self._dll)

        self.cable = _Cable(self._dll)

        self.grp_data = _GroupData(self._dll)
        self.grp_lc_data = _GroupLCData(self._dll)
        self.sec_grp_lc_data = _SecondaryGroupLCData(self._dll)

        self.nodes = _Nodes(self._dll)

        self.plate_data = _PlateData(self._dll)

        self.spring = _Spring(self._dll)

        self.load_case = _LoadCases(self._dll)
        self.properties = _PropertyData(self._dll)

        self.truss = _Truss(self._dll)

    def clear(self) -> None:
        """Clear all the loaded data and results.
        """
        #self.beam_res.clear_all_forces()
        #self.beam_geo.clear_connectivity()
        self.cable.data.clear()
        self.cable.load.clear_all()
        self.cable.result.clear_all()
        self.grp_data.clear()
        self.grp_lc_data.clear_all()
        self.sec_grp_lc_data.clear_all()
        self.nodes.data.clear()
        self.nodes.results.clear_all()
        self.spring.data.clear()
        self.spring.result.clear_all()
        #self.load_case.clear_all()
        #self.properties.clear_all_values()

    def clear_data(self) -> None:
        """Clear all the loaded data.
        """
        #self.beam_geo.clear_connectivity()
        self.cable.data.clear()
        self.grp_data.clear()
        self.grp_lc_data.clear_all()
        self.sec_grp_lc_data.clear_all()
        self.nodes.data.clear()
        self.spring.data.clear()
        #self.load_case.clear_all()
        #self.properties.clear_all_values()

    def clear_results(self) -> None:
        """Clear all the loaded results.
        """
        #self.beam_res.clear_all_forces()
        self.cable.result.clear_all()
        self.nodes.results.clear_all()
        self.spring.result.clear_all()
        #self.load_case.clear_all()

    def close(self) -> None:
        """Close the CDB database.
        """
        self._dll.close()
        self.is_open = False

    def get_echo_level(self) -> int:
        """return the ``echo_level`` for this instance of ``SOFiSTiKCDBReader``.
        """
        return self._echo_level

    def initialize(self) -> None:
        """Open the CDB file.
        """
        self.open()

    def open(self) -> None:
        """Open a CDB database always in a read-only mode! This method is supposed to be
        called before any other call.
        """
        if not self.is_open:
            self._dll.initialize()
            self._dll.open_cdb(self.full_name, 93)
            self.is_open = True

    def set_echo_level(self, new_echo_level: int) -> None:
        """Set the ``echo_level`` for this instance of ``SOFiSTiKCDBReader``.
        """
        self._echo_level = new_echo_level
        self._dll.set_echo_level(new_echo_level)
