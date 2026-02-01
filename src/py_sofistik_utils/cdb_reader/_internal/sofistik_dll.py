"""
SofDll
------

The `_SofDll` class load the SOFiSTiK dll `sof_cdb_w-202X.dll` and store as member
variables some of the function provided by SOFiSTiK to read and write cdb files.

Writing to a cdb is currently not supported.
"""
# standard library imports
from ctypes import cdll, CDLL
from os import add_dll_directory
from os.path import isfile
from pathlib import Path
from typing import Callable

# third party library imports

# local library specific imports
from . sofistik_utilities import decode_cdb_status


class SofDll():
    """The `_SofDll` class load the SOFiSTiK dll `sof_cdb_w-202X.dll` and store as member
    variables some of the function provided by SOFiSTiK to read cdb files.
    """
    def __init__(self, dll_folder: str, echo_level: int = 0, version: int = 2023) -> None:
        """The initializer of the `SofDll` class.
        """
        self._dll: CDLL
        self.get: Callable[..., int]

        self._echo_level = echo_level
        self._path: str = dll_folder if self._check_folder(dll_folder) else ""
        self._version: str = self._check_version(version)

    def close(self) -> None:
        """Close the CDB database.
        """
        self._dll.sof_cdb_close(1)

        if self._dll.sof_cdb_status(1) == 0:
            print("CDB file has been successfully closed.")
            return

        raise RuntimeError("Unknown error while closing cdb file!")

    def load_dll(self) -> bool:
        """Checks if all the required required SOFiSTiK dynamic libraries are present and
        loads the main SOFiSTiK dll.
        Returns `True` on success.
        """
        if not self._check_folder(self._path):
            raise RuntimeError()
            return False

        if not self._check_files(self._path, ["libmmd.dll", "libifcoremd.dll"]):
            raise RuntimeError()
            return False

        if not self._check_files(self._path, [self._version]):
            raise RuntimeError()
            return False
        print("\n")
        try:
            with add_dll_directory(self._path):
                print(1)
                print("Library loaded successfully!")
                self._dll = cdll.LoadLibrary(self._version)

        except: # OSError as e:
            print(f"Failed to load library: {1}")
            raise RuntimeError

        return True

    def get_echo_level(self) -> int:
        """Return the `echo_level` of this instance of `SofDll`.
        """
        return self._echo_level

    def initialize(self) -> None:
        """
        """
        self.load_dll()

        self.get = self._dll.sof_cdb_get

    def key_exist(self, kwh: int, kwl: int) -> bool:
        """Return `True` if the key exists and contains data, `False` otherwise.
        """
        match self._dll.sof_cdb_kexist(kwh, kwl):
            case 0:
                if self._echo_level > 0:
                    print(f"Key {kwh}/{kwl} does not exist!")
                return False

            case 1:
                if self._echo_level > 0:
                    print(f"Key {kwh}/{kwl} exists, but it's empty!")
                return False

            case 2:
                return True

            case _:
                if self._echo_level > 0:
                    print(f"Unknown error in checking existance of key {kwh}/{kwl}!")
                return False

    def open_cdb(self, file_full_name: str, mode: int = 93) -> None:
        """Open the cdb file give its full name.

        Parameters
        ----------
        file_full_name: str
            Absolute path to the cdb file.
        mode: int, optional and default to 93
            Read only access with mode = 93.
        """
        if not isfile(file_full_name):
            raise RuntimeError(f"\"{file_full_name}\" is NOT an existing regular file!")

        self._dll.sof_cdb_init(file_full_name.encode("UTF-8"), mode)

        if self._dll.sof_cdb_status(1) > 0:
            if self._echo_level > 0:
                print(f"CDB \"{file_full_name}\" successfully opened.")
                print(decode_cdb_status(self._dll.sof_cdb_status(1)))

            return

        raise RuntimeError(f"Unknown error while opening \"{file_full_name}\"!")

    def set_echo_level(self, echo_level: int) -> None:
        """Set the `echo_level` for this instance of `SofDll`.
        """
        self._echo_level = echo_level

    @staticmethod
    def _check_files(path_to_dll: str, files: list[str]) -> bool:
        """Returns `True` if all the listed files are found in the provided folder.
        """
        return all((Path(path_to_dll) / _).is_file() for _ in files)

    @staticmethod
    def _check_folder(path_to_dll: str) -> bool:
        """Returns `True` if the provided path is a valid folder.
        """
        return Path(path_to_dll).is_dir()

    @staticmethod
    def _check_version(version: int) -> str:
        """Return the name of the SOFiSTiK dll to be loaded given the software version.
        """
        if version in [2022, 2023, 2024, 2025]:
            return f"sof_cdb_w-{version}.dll"

        raise RuntimeError("Supported SOFiSTiK versions: 2022, 2023, 2024 and 2025!")
