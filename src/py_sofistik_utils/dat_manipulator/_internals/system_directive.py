"""
SOFiSTiKSystemDirective
-----------------------

The `SOFiSTiKSystemDirective` is an auxiliary class that manage a SOFiSTiK sys directive.

__author__ = "Studio W Engineers"

__version__ = "0.1.0"

__maintainer__ = "Studio W Engineers"

__email__ = "studio.w.engineers@gmail.com"

__status__ "Alpha"
"""
# standard library imports

# third party library imports
from sw_core.data_types.mutable_string import MutableString

# local library specific imports


def is_system_directive(string: str | MutableString) -> bool:
    """Return `True` if the given string fits in a SOFiSTiK `SOFiSTiKSystemDirective`
    definition.
    """
    if isinstance(string, MutableString):
        string = string.to_string()

    return string.lstrip().upper()[1:4] == "SYS"


class SOFiSTiKSystemDirective:
    """Auxiliary class that manages a SOFiSTiK sys directive.
    """
    def __init__(self, content: MutableString) -> None:
        """The initializer of the `SOFiSTiKSystemDirective` class.

        The `from_string` method is supposed to be used to create instances of this class,
        which performs additional checks on the content.
        """
        content.upper()
        self._content = content

        self._is_linked = False
        self._is_off = False
        self._is_on = False

        # detect status
        match self._content[self._content.find("SYS") - 1]:
            case "*":
                self._is_linked = True
            case "-":
                self._is_off = True
            case "+":
                self._is_on = True
            case _:
                raise RuntimeError(f"Illegal SYS directive:\n{content}")

    def __eq__(self, value: object) -> bool:
        if isinstance(value, SOFiSTiKSystemDirective):
            return self._content.to_string() == value._content.to_string()
            # here it should not be required to use to_string --> __eq__ is implemented in
            # MutableString

        return False

    def __repr__(self) -> str:
        return "SOFiSTiK sys directive with content:\n" + self.serialize()

    def get_content(self) -> MutableString:
        """Return the content of the sys directive as a `MutableString`.
        """
        return self._content

    def get_content_as_string(self) -> str:
        """Return the content of the sys directive as a `str`.
        """
        return self._content.to_string()

    def is_linked(self) -> bool:
        """Return `True` if the execution is linked to the last PROG line.
        """
        return self._is_linked

    def is_off(self) -> bool:
        """Return `True` if the execution is turned off.
        """
        return self._is_off

    def is_on(self) -> bool:
        """Return `True` if the execution is turned on.
        """
        return self._is_on

    def link_to_prog(self) -> None:
        """Link the execution of the `SOFiSTiKSystemDirective` to the last PROG line.
        """
        if not self._is_linked:
            self._content[self._content.find("-" if self._is_off else "+")] = "*"
            self._is_linked = True
            self._is_off = self._is_on = False

    def turn_off(self) -> None:
        """Turn off the `SOFiSTiKSystemDirective`.
        """
        if not self._is_off:
            self._content[self._content.find("+" if self._is_on else "*")] = "-"
            self._is_off = True
            self._is_linked = self._is_on = False

    def turn_on(self) -> None:
        """Turn on the `SOFiSTiKSystemDirective`.
        """
        if not self._is_on:
            self._content[self._content.find("-" if self._is_off else "*")] = "+"
            self._is_on = True
            self._is_linked = self._is_off = False

    def serialize(self) -> str:
        """Serialize the content of this `SOFiSTiKSystemDirective` instance.
        """
        return self._content.to_string()

    @classmethod
    def from_string(cls, content: str) -> "SOFiSTiKSystemDirective":
        """Create an instance of `SOFiSTiKSystemDirective` from the given content`.
        The string is converted to uppercase and trailing whitespaces are removed.
        """
        if content.lstrip().rstrip().upper()[1:4] != "SYS":
            raise RuntimeError(
                f"SOFiSTiKSystemDirective must start with \"SYS\":\n{content}!"
            )

        return cls(MutableString(content.rstrip().upper()))
