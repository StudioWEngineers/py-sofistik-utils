# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CSPRI_RES


class _SpringResults:
    """The ``_SpringResults`` class provides methods and data structure to:

    * access and load the keys ``170/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "FORCE",
                "TRANSVERSAL_FORCE",
                "MOMENT",
                "DISPLACEMENT",
                "TRANSVERSAL_DISPLACEMENT",
                "ROTATION"
            ]
        )
        self._dll = dll
        self._echo_level = 0
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the loaded data for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data[
            self._data.index.get_level_values("LOAD_CASE") != load_case
        ]
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear the loaded data for all the load cases.
        """
        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def load(self, load_case: int, grp_divisor: int = 10000) -> None:
        """Load the results for the given ``load_case``.
        """
        if self._dll.key_exist(170, load_case):
            spring = CSPRI_RES()
            record_length = c_int(sizeof(spring))
            return_value = c_int(0)

            if load_case not in self._loaded_lc:
                self._displacements[load_case] = {}
                self._forces[load_case] = {}
                self._moment[load_case] = {}
                self._rotation[load_case] = {}

            else:
                self.clear(load_case)

            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    170,
                    load_case,
                    byref(spring),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                spring_nmb: int = spring.m_nr
                if spring_nmb == 0:
                    record_length = c_int(sizeof(spring))
                    count += 1
                    continue

                grp_nmp = spring.m_nr // grp_divisor

                if grp_nmp not in self._displacements[load_case]:
                    self._displacements[load_case].update({grp_nmp: {}})
                    self._forces[load_case].update({grp_nmp: {}})
                    self._moment[load_case].update({grp_nmp: {}})
                    self._rotation[load_case].update({grp_nmp: {}})

                self._displacements[load_case][grp_nmp].update(
                    {spring_nmb: array([spring.m_v,
                                           spring.m_vt,
                                           spring.m_vtx,
                                           spring.m_vty,
                                           spring.m_vtz], dtype = float64)})

                self._rotation[load_case][grp_nmp].update({spring_nmb: spring.m_phi})

                self._forces[load_case].update(
                    {spring_nmb: array(
                        [spring.m_p,
                         spring.m_pt,
                         spring.m_ptx,
                         spring.m_pty,
                         spring.m_ptz], dtype = float64)})

                self._moment[load_case].update({spring_nmb: spring.m_m})

                record_length = c_int(sizeof(spring))
                count += 1

            self._loaded_lc.add(load_case)

    def get_element_displacements(
            self,
            load_case: int,
            spring_nmb: int
        ) -> NDArray[float64]:
        """Return the spring displacements for the given ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``spring_nmb``: int
            Spring number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``spring_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        for group_result in self._displacements[load_case].values():
            if spring_nmb in group_result:
                return group_result[spring_nmb]

        err_msg = f"Element number {spring_nmb} not found in load case {load_case}!"
        raise RuntimeError(err_msg)

    def get_element_rotation( self, load_case: int, spring_nmb: int) -> float:
        """Return the spring rotation for the given ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``spring_nmb``: int
            Spring number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``spring_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        for group_result in self._rotation[load_case].values():
            if spring_nmb in group_result:
                return group_result[spring_nmb]

        err_msg = f"Spring number {spring_nmb} not found in load case {load_case}!"
        raise RuntimeError(err_msg)
