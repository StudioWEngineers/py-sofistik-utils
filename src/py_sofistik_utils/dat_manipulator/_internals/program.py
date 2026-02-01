"""
SOFiSTiKProgram
---------------

The `SOFiSTiKProgram` is an auxiliary class that manage a SOFiSTiK program.

__author__ = "Studio W Engineers"

__version__ = "0.1.0"

__maintainer__ = "Studio W Engineers"

__email__ = "studio.w.engineers@gmail.com"

__status__ "Alpha"
"""
# standard library imports
from copy import deepcopy

# third party library imports
from sw_core.data_types.mutable_string import MutableString

# local library specific imports


_sofistik_types: list[str] = ["AQB",
                              "AQUA",
                              "ASE",
                              "MAXIMA",
                              "RESULTS",
                              "SOFILOAD",
                              "SOFIMSHA",
                              "SOFIMSHB",
                              "SOFIMSHC",
                              "TEMPLATE",
                              "WING"]


class SOFiSTiKProgram:
    """Auxiliary class that manages a SOFiSTiK program.
    """
    def __init__(
            self,
            content: list[MutableString],
            name: str = "NEW PROGRAM",
            is_active: bool = False,
            prg_type: str = "ASE"
        ) -> None:
        """The initializer of the `Program` class.
        """
        self._content: list[MutableString] = content
        self._is_active: bool = is_active
        self._name: str = name.upper()
        self._type: str = prg_type

        self._detect_is_active()
        self._detect_type()

    def __repr__(self) -> str:
        return (f"{self._type} SOFiSTiK program \"{self._name}\" with content:\n" +
                self.serialize())

    def add_row(self, row: str | MutableString) -> None:
        """Add a row at the end of the program.
        """
        if isinstance(row, MutableString):
            row.upper()
            self._content.append(row)
        elif isinstance(row, str):
            self._content.append(MutableString(row.upper()))
        else:
            raise TypeError("Row must be an instance of \"str\" or \"MutableString\", "
                            f"given of type {type(row)}!")

    def add_row_after(self, new_row: str, target_row: str) -> None:
        """Insert the given `new_row` after the `target_row`.

        Parameters
        ----------
        new_row : str
        target_row : str

        Raises
        ------
        ValueError
            If the `target_row` is not found.
        """
        self._content.insert(self.get_row_index(target_row) + 1,
                             MutableString(new_row.upper().rstrip()))

    def add_row_before(self, new_row: str, target_row: str) -> None:
        """Insert the given `new_row` before the `target_row`.

        Parameters
        ----------
        new_row : str
        target_row : str

        Raises
        ------
        ValueError
            If the `target_row` is not found.
        """
        self._content.insert(self.get_row_index(target_row),
                             MutableString(new_row.upper().rstrip()))

    def clear(self) -> None:
        """Clear the content, type and name of this `Program`.
        """
        self._content.clear()
        self._name = ""
        self._type = ""

    def get_content(self) -> list[MutableString]:
        """Return a `deepcopy` of the content of this `Program`.
        """
        return deepcopy(self._content)

    def get_name(self) -> str:
        """Return the name of this `Program`."
        """
        return self._name

    def get_number_of_rows(self) -> int:
        """Return the number of rows of this `Program`.
        """
        return len(self._content)

    def get_row_by_index(self, index: int) -> MutableString:
        """Return a shallow copy of the row of the given `index`.

        Parameters
        ----------
        index : int

        Raises
        ------
        IndexError
            If the `index` is not found.
        """
        try:
            return self._content[index]

        except IndexError as exc:
            err_msg = f"Index \"{index}\" has not been found in Program \"{self._name}\"!"
            raise IndexError(err_msg) from exc

    def get_row_index(self, row: str) -> int:
        """Return the first index corresponding to the given `row`.

        Parameters
        ----------
        row : str

        Raises
        ------
        ValueError
            If the `row` is not found.
        """
        try:
            return self._content.index(MutableString(row.rstrip().upper()))

        except ValueError as exc:
            err_msg = f"Row \"{row}\" has not been found in Program \"{self._name}\"!"
            raise ValueError(err_msg) from exc

    def get_type(self) -> str:
        """Return the type of this SOFiSTiK `Program` instance.
        """
        return self._type

    def is_active(self) -> bool:
        """Return the status of this SOFiSTiK `Program` instance.
        """
        return self._is_active

    def modify_row(self, row_index: int, new_row: str) -> None:
        """Change the content of the row with index `row_index` to `new_row`.
        """
        self._content[row_index] = MutableString(new_row.rstrip().upper())

    def remove_row_by_index(self, index: int) -> None:
        """Remove the row corresponding to the given global `index`.

        Parameters
        ----------
        index : int

        Raises
        ------
        IndexError
            If the `index` is not found.
        """
        try:
            del self._content[index]

        except IndexError as exc:
            err_msg = f"Index \"{index}\" has not been found in Program \"{self._name}\"!"
            raise IndexError(err_msg) from exc

    def remove_row_by_text(self, row: str) -> None:
        """"Remove the given `row` from the program.

        Parameters
        ----------
        row : str

        Raises
        ------
        ValueError
            If the `row` is not found.
        """
        try:
            index = self._content.index(MutableString(row.upper()))
            del self._content[index]

        except ValueError as exc:
            err_msg = f"Row \"{row}\" has not been found in Program \"{self._name}\"!"
            raise ValueError(err_msg) from exc

    def replace(self, old_row: str, new_row: str) -> None:
        """Replace the `old_row` with the given `new_row`.

        Parameters
        ----------
        old_row : str
        new_row : str

        Raises
        ------
        ValueError
            If the `old_row` is not found.
        """
        index = self.get_row_index(old_row)

        self._content.insert(index, MutableString(new_row.upper()))
        del self._content[index + 1]

    def replace_by_index(self, index: int, new_row: str) -> None:
        """Replace the row with the given `index` with the `new_row`.

        Parameters
        ----------
        index : int
        new_row : str

        Raises
        ------
        IndexError
            If the `index` exceeds the list boundaries.
        """
        self._content.insert(index, MutableString(new_row.upper().rstrip()))
        del self._content[index + 1]

    def serialize(self) -> str:
        """Serialize the content of this `SOFiSTiKProgram` instance.
        """
        return "".join([_.to_string() + "\n" for _ in self._content]).rstrip()

    def set_name(self, new_name: str) -> None:
        """Set the program name to the given one.
        """
        self.replace_by_index(1, "HEAD " + new_name.upper())
        self._name = new_name.upper()

    def set_type(self, prog_type: str) -> None:
        """Set the program type to the given one.
        """
        if prog_type.upper() not in _sofistik_types:
            err_msg = f"Program type \"{prog_type}\" is not valid!\n"
            err_msg += f"Valid program types are: {_sofistik_types}."
            raise RuntimeError(err_msg)

        flag = "+" if self.is_active() else "-"
        self.replace_by_index(0, flag + "PROG " + prog_type.upper())
        self._type = prog_type.upper()

    def turn_off(self) -> None:
        """Turn off this SOFiSTiK `Program` instance.
        """
        self.get_row_by_index(0)[0] = "-"
        self._is_active = False

    def turn_on(self) -> None:
        """Turn on this SOFiSTiK `Program` instance.
        """
        self.get_row_by_index(0)[0] = "+"
        self._is_active = True

    def _detect_is_active(self) -> None:
        """Detect if this SOFiSTiK `Program` instance is active or not.
        """
        if self._content:
            match self._content[0][0]:
                case "+":
                    self.turn_on()
                case "-":
                    self.turn_off()
                case _:
                    raise RuntimeError("Program first character must be \"+\" or \"-\"!")

    def _detect_type(self) -> None:
        """Detect the type of this SOFiSTiK `Program` instance.
        """
        if self._content:
            sofistik_type = self._content[0].split()[1]

            if sofistik_type not in _sofistik_types:
                err_msg = f"Program type \"{sofistik_type}\" is not valid!\n"
                err_msg += f"Valid program types are: {_sofistik_types}."
                raise RuntimeError(err_msg)

            self._type = sofistik_type

    @classmethod
    def create_empty(cls,
                     name: str,
                     prog_type: str = "ASE",
                     is_active: bool = True
        ) -> "SOFiSTiKProgram":
        """Create a new empty `SOFiSTiKProgram` instance.
        """
        obj = cls([], name)

        obj._content.append(MutableString("-PROG ASE"))
        obj._content.append(MutableString("\tHEAD " + name.upper()))
        obj._content.append(MutableString("END"))

        obj.set_type(prog_type)
        if is_active:
            obj.turn_on()

        return obj

    @staticmethod
    def count_row(search_string: str, search_list: list[MutableString]) -> int:
        """Return the number of occurrences of `search_string` in `search_list`.

        Parameters
        ----------
        search_string : str
            the search string

        search_list : list[MutableString]
            the search list

        Returns
        -------
        int
            Number of occurrences of `search_string`.

        Raises
        ------
        TypeError
            If the `search_string` is not of type `str`.
        """
        if not isinstance(search_string, str):
            err_msg = ("Search string must be a str, given of type "
                       f"\"{type(search_string)}\"!")
            raise TypeError(err_msg)

        return [_.to_string() for _ in search_list].count(search_string.upper())
