# standard library imports
import os
from ctypes import CDLL, cdll
from pathlib import Path
from typing import Callable

# third party library imports

# local library specific imports
from . sofistik_utilities import decode_cdb_status


class SofDll():
    """This class loads the SOFiSTiK DLL `sof_cdb_w-202X.dll` and stores, as
    member variables, selected functions provided by SOFiSTiK for reading CDB
    files.
    """
    def __init__(
            self,
            dll_folder: str,
            echo_level: int = 0,
            version: int | str = 2023
    ) -> None:
        self.get: Callable[..., int]
        self.key_exist: Callable[..., bool]
        self.to_string: Callable[..., str]

        self._dll: CDLL
        self._echo_level = echo_level
        self._path: str = dll_folder if self._check_folder(dll_folder) else ""
        self._version: str = self._check_version(version)

    def close(self) -> None:
        """Close the CDB database.
        """
        self._dll.sof_cdb_close(0)  # 0 to close all files
        if self._dll.sof_cdb_status(1) != 0:
            raise RuntimeError("Unknown error while closing cdb file!")
        if self._echo_level > 0:
            print("CDB file has been successfully closed.")

    def get_echo_level(self) -> int:
        """Return the `echo_level` of this instance of `SofDll`.
        """
        return self._echo_level

    def initialize(self) -> None:
        """Load the SOFiSTiK dll.
        """
        if not self._check_folder(self._path):
            raise RuntimeError(
                f"The provided {self._path} is not a valid directory!"
            )

        if not self._check_files(
            self._path,
            ["libmmd.dll", "libifcoremd.dll"]
        ):
            raise RuntimeError("libmmd.dll or libifcoremd.dll not found!")

        if not self._check_files(self._path, [self._version]):
            raise RuntimeError(f"{self._version} not found!")

        try:
            with os.add_dll_directory(self._path):
                self._dll = cdll.LoadLibrary(self._version)
        except Exception as e:
            print(f"Failed to load {self._version} in {self._path}!")
            raise RuntimeError() from e

        self.get = self._dll.sof_cdb_get
        self.key_exist = self._dll.sof_cdb_kexist
        self.to_string = self._dll.sof_lib_ps2cs

    def open_cdb(self, file_full_name: str) -> None:
        """Open the cdb file in read-only mode.
        """
        if not os.path.isfile(file_full_name):
            raise RuntimeError(
                f"\"{file_full_name}\" is NOT an existing regular file!"
            )

        self._dll.sof_cdb_init(file_full_name.encode("UTF-8"), 93)

        if self._dll.sof_cdb_status(1) > 0:
            if self._echo_level > 0:
                print(f"CDB \"{file_full_name}\" successfully opened.")
                print(decode_cdb_status(self._dll.sof_cdb_status(1)))
            return

        raise RuntimeError(
            f"Unknown error while opening \"{file_full_name}\"!"
        )

    def set_echo_level(self, echo_level: int) -> None:
        """Set the `echo_level` for this instance of `SofDll`.
        """
        self._echo_level = echo_level

    @staticmethod
    def _check_files(path_to_dll: str, files: list[str]) -> bool:
        """Returns `True` if all the given files are found in `path_to_dll`.
        """
        return all((Path(path_to_dll) / _).is_file() for _ in files)

    @staticmethod
    def _check_folder(path_to_dll: str) -> bool:
        """Returns `True` if the provided path is a valid folder.
        """
        return Path(path_to_dll).is_dir()

    @staticmethod
    def _check_version(version: int | str) -> str:
        """Return the name of the SOFiSTiK dll to be loaded, given the version.
        """
        if isinstance(version, int):
            version = str(version)

        if version in ["2022", "2023", "2024", "2025"]:
            return f"sof_cdb_w-{version}.dll"

        raise RuntimeError(
            "Supported SOFiSTiK versions: 2022, 2023, 2024 and 2025!"
        )
