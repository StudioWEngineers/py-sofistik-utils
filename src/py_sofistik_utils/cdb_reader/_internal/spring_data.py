"""
SpringData
----------

The `SpringData` class provides methods and data structure to:
    * access and load the key `170/00` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
"""
# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CSPRI


class SpringData:
    """The `SpringData` class provides methods and data structure to:
    * access and load the key `170/00` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `SpringData` class.
        """
        self._dll = dll

        self._axial_stiffness: dict[int, dict[int, float]] = {}
        self._connectivity: dict[int, dict[int, list[int]]] = {}
        self._lateral_stiffness: dict[int, dict[int, float]] = {}
        self._rotational_stiffness: dict[int, dict[int, float]] = {}

    def clear(self) -> None:
        """Clear all the spring data for all the spring elements and groups.
        """
        self._axial_stiffness.clear()
        self._connectivity.clear()
        self._lateral_stiffness.clear()
        self._rotational_stiffness.clear()

    def load(self, group_divisor: int = 10000) -> None:
        """Load the spring data.
        """
        if self._dll.key_exist(170, 0):
            spring = CSPRI()
            rec_length = c_int(sizeof(spring))
            return_value = 0

            self.clear()

            count = 0
            while return_value < 2:
                return_value = self._dll.get(
                    1,
                    170,
                    0,
                    byref(spring),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                spring_nmb: int = spring.m_nr
                grp_nmb = spring_nmb // group_divisor

                if grp_nmb not in self._connectivity:
                    self._axial_stiffness[grp_nmb] = {}
                    self._connectivity[grp_nmb] = {}
                    self._lateral_stiffness[grp_nmb] = {}
                    self._rotational_stiffness[grp_nmb] = {}

                self._axial_stiffness[grp_nmb].update({spring_nmb: spring.m_cp})
                self._connectivity[grp_nmb].update({spring_nmb: list(spring.m_node)})
                self._lateral_stiffness[grp_nmb].update({spring_nmb: spring.m_cq})
                self._rotational_stiffness[grp_nmb].update({spring_nmb: spring.m_cm})

                rec_length = c_int(sizeof(spring))
                count += 1

    def get_element_connectivity(self, spring_nmb: int) -> list[int]:
        """Return the connectivity for the given `spring_nmb`.

        Parameters
        ----------
        `spring_nmb`: int
            The sprig element number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        for group_data in self._connectivity.values():
            if spring_nmb in group_data:
                return group_data[spring_nmb]

        raise RuntimeError(f"Element number {spring_nmb} not found!")

    def get_element_axial_stiffness(self, spring_nmb: int) -> float:
        """Return the spring axial stiffness for the given `spring_nmb`.

        Parameters
        ----------
        `spring_nmb`: int
            The sprig element number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        for group_data in self._axial_stiffness.values():
            if spring_nmb in group_data:
                return group_data[spring_nmb]

        raise RuntimeError(f"Element number {spring_nmb} not found!")

    def get_element_lateral_stiffness(self, spring_nmb: int) -> float:
        """Return the spring lateral stiffness for the given `spring_nmb`.

        Parameters
        ----------
        `spring_nmb`: int
            The sprig element number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        for group_data in self._lateral_stiffness.values():
            if spring_nmb in group_data:
                return group_data[spring_nmb]

        raise RuntimeError(f"Element number {spring_nmb} not found!")

    def get_element_rotational_stiffness(self, spring_nmb: int) -> float:
        """Return the spring rotational stiffness for the given `spring_nmb`.

        Parameters
        ----------
        `spring_nmb`: int
            The sprig element number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        for group_data in self._rotational_stiffness.values():
            if spring_nmb in group_data:
                return group_data[spring_nmb]

        raise RuntimeError(f"Element number {spring_nmb} not found!")

    def has_axial_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has an axial stiffness `!= 0`.

        Parameters
        ----------
        `spring_nmb`: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        return self.get_element_axial_stiffness(spring_nmb) != 0.0

    def has_lateral_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has a lateral stiffness `!= 0`.

        Parameters
        ----------
        `spring_nmb`: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        return self.get_element_lateral_stiffness(spring_nmb) != 0.0

    def has_rotational_stiffness(self, spring_nmb: int) -> bool:
        """Return `True` if the spring has a rotational stiffness != 0.

        Parameters
        ----------
        `spring_nmb`: int
            The spring number

        Raises
        ------
        RuntimeError
            If the given `spring_nmb` is not found.
        """
        return self.get_element_rotational_stiffness(spring_nmb) != 0.0
