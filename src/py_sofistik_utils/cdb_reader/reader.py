"""
SOFiSTiKCDBReader
-----------------

The ``SOFiSTiKCDBReader`` class provides methods and data structure to read-only access to a
SOFiSTiK cdb file and serialize its content.
"""
# standard library imports

# third party library imports

# local library specific imports
from . _internal.beam_data import _BeamData
from . _internal.beam_load import BeamLoad
from . _internal.beam_results import BeamResults
from . _internal.beam_stresses import BeamStress
from . _internal.cable_data import CableData
from . _internal.cable_load import CableLoad
from . _internal.cable_results import CableResults
from . _internal.group_data import GroupData
from . _internal.group_lc_data import GroupLCData
from . _internal.load_cases import _LoadCases
from . _internal.nodes import _Nodes
from . _internal.plate_data import PlateData
from . _internal.property import PropertyData
from . _internal.sec_group_lc_data import SecondaryGroupLCData
from . _internal.spring_data import SpringData
from . _internal.spring_results import SpringResults
from . _internal.sofistik_dll import SofDll
from . _internal.sys_info import SysInfo
from . _internal.truss_data import _TrussData
from . _internal.truss_load import _TrussLoad
from . _internal.truss_results import _TrussResult


class SOFiSTiKCDBReader:
    """The ``SOFiSTiKCDBReader`` class provides methods and data structure to read-only
    access to a SOFiSTiK cdb file and serialize its content.
    """
    beam_geo: _BeamData
    load_case: _LoadCases
    nodes: _Nodes
    truss_data: _TrussData
    truss_load: _TrussLoad
    truss_results: _TrussResult

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

        self.beam_res = BeamResults(self._dll)
        self.beam_geo = _BeamData(self._dll)
        self.beam_load = BeamLoad(self._dll)
        self.beam_stress = BeamStress(self._dll)

        self.cable_data = CableData(self._dll)
        self.cable_load = CableLoad(self._dll)
        self.cable_res = CableResults(self._dll)

        self.grp_data = GroupData(self._dll)
        self.grp_lc_data = GroupLCData(self._dll)
        self.sec_grp_lc_data = SecondaryGroupLCData(self._dll)

        self.nodes = _Nodes(self._dll)

        self.plate_data = PlateData(self._dll)

        self.spring_data = SpringData(self._dll)
        self.spring_res = SpringResults(self._dll)

        self.load_case = _LoadCases(self._dll)
        self.properties = PropertyData(self._dll)
        self.sys_info = SysInfo(self._dll)

        self.truss_data = _TrussData(self._dll)
        self.truss_load = _TrussLoad(self._dll)
        self.truss_results = _TrussResult(self._dll)

    def clear(self) -> None:
        """Clear all the loaded data and results.
        """
        #self.beam_res.clear_all_forces()
        #self.beam_geo.clear_connectivity()
        self.cable_data.clear()
        self.cable_load.clear_all()
        self.cable_res.clear_all()
        self.grp_data.clear()
        self.grp_lc_data.clear_all()
        self.sec_grp_lc_data.clear_all()
        self.nodes.data.clear()
        self.nodes.results.clear_all()
        self.spring_data.clear()
        self.spring_res.clear_all()
        #self.load_case.clear_all()
        #self.properties.clear_all_values()
        #self.sys_info.clear()

    def clear_data(self) -> None:
        """Clear all the loaded data.
        """
        #self.beam_geo.clear_connectivity()
        self.cable_data.clear()
        self.grp_data.clear()
        self.grp_lc_data.clear_all()
        self.sec_grp_lc_data.clear_all()
        self.nodes.data.clear()
        self.spring_data.clear()
        #self.load_case.clear_all()
        #self.properties.clear_all_values()
        #self.sys_info.clear()

    def clear_results(self) -> None:
        """Clear all the loaded results.
        """
        #self.beam_res.clear_all_forces()
        self.cable_res.clear_all()
        self.nodes.results.clear_all()
        self.spring_res.clear_all()
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
