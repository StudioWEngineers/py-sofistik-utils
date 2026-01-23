"""
SysInfo
-------

The `SysInfo` class provides methods and data structure to:
    * access the key 10/0 of the cdb file;
    * store these information in a convenient format;
    * provide API to access these information.
"""
# standard library imports
from ctypes import byref, create_string_buffer, c_int, sizeof

# third party library imports

# local library specific imports
from . sofistik_classes import CSYST
from . sofistik_dll import SofDll


class SysInfo:
    """The `SysInfo` class provides methods and data structure to:
    * access the key 10/0 of the cdb file;
    * store these information in a convenient format;
    * provide API to access these information.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `SysInfo` class.
        """
        self._dll = dll
        self._info: dict[str, str | int] = {}

    def clear(self) -> None:
        """Clear the system information.
        """
        self._info.clear()

    def gravity_direction(self) -> str:
        """Return the gravity direction. `load` method is supposed to be called
        beforehand.

        Raises
        ------
        KeyError
            If the system informations have not been loaded.
        """
        try:
            if isinstance(self._info["GRAVITY_DIRECTION"], str):
                return self._info["GRAVITY_DIRECTION"]

            raise TypeError("Unexpected type for \"GRAVITY_DIRECTION\"!")

        except KeyError as exc:
            raise KeyError("System informations have not been loaded!") from exc

    def group_divisor(self) -> int:
        """Return the group divisor number. `load` method is supposed to be called
        beforehand.

        Raises
        ------
        KeyError
            If the system informations have not been loaded.
        """
        try:
            if isinstance(self._info["GROUP_DIVISOR"], int):
                return self._info["GROUP_DIVISOR"]

            raise TypeError("Unexpected type for \"GROUP_DIVISOR\"!")

        except KeyError as exc:
            raise KeyError("System informations have not been loaded!") from exc

    def load(self) -> None:
        """Load the system information.
        """
        match self._dll.key_exist(10, 0):
            case 0:
                raise RuntimeError("Key 10/0 does not exist!")

            case 1:
                raise RuntimeError("Key 10/0 exists, but does not contain data!")

            case 2:
                info = CSYST()
                record_length = c_int(sizeof(info))
                return_value = c_int(0)

                self.clear()

                return_value.value = self._dll.get(
                    1,
                    10,
                    0,
                    byref(info),
                    byref(record_length),
                    0
                )

                name = create_string_buffer(64 * 4)
                self._dll.to_string(byref(info.m_txt), byref(name), sizeof(name))

                self._info.update({"PROJECT_NAME": name.value.decode()})
                self._info.update({"NUMBER_OF_NODES": info.m_nknot})
                self._info.update({"MAX_NODE_ID": info.m_mknot})
                self._info.update({"GROUP_DIVISOR": info.m_igdiv})

                match info.m_iachs:
                    case 0:
                        direction = "UNDEFINED"
                    case -1:
                        direction = "NEGATIVE X-AXIS"
                    case -2:
                        direction = "NEGATIVE Y-AXIS"
                    case -3:
                        direction = "NEGATIVE Z-AXIS"
                    case 1:
                        direction = "POSITIVE X-AXIS"
                    case 2:
                        direction = "POSITIVE Y-AXIS"
                    case 3:
                        direction = "POSITIVE Z-AXIS"
                    case _:
                        raise RuntimeError("Unexpected value for gravity direction!")

                self._info.update({"GRAVITY_DIRECTION": direction})

            case _:
                raise RuntimeError("Unknown error while checking existance of key 10/0")

    def max_node_id(self) -> int:
        """Return the maximum node ID. `load` method is supposed to be called beforehand.

        Raises
        ------
        KeyError
            If the system informations have not been loaded.
        """
        try:
            if isinstance(self._info["MAX_NODE_ID"], int):
                return self._info["MAX_NODE_ID"]

            raise TypeError("Unexpected type for \"MAX_NODE_ID\"!")

        except KeyError as exc:
            raise KeyError("System informations have not been loaded!") from exc

    def number_of_nodes(self) -> int:
        """Return the number of nodes. `load` method is supposed to be called beforehand.

        Raises
        ------
        KeyError
            If the system informations have not been loaded.
        """
        try:
            if isinstance(self._info["NUMBER_OF_NODES"], int):
                return self._info["NUMBER_OF_NODES"]

            raise TypeError("Unexpected type for \"NUMBER_OF_NODES\"!")

        except KeyError as exc:
            raise KeyError("System informations have not been loaded!") from exc

    def project_name(self) -> str:
        """Return the project name. `load` method is supposed to be called beforehand.

        Raises
        ------
        KeyError
            If the system informations have not been loaded.
        """
        try:
            if isinstance(self._info["PROJECT_NAME"], str):
                return self._info["PROJECT_NAME"]

            raise TypeError("Unexpected type for \"PROJECT_NAME\"!")

        except KeyError as exc:
            raise KeyError("System informations have not been loaded!") from exc
