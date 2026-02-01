"""
SOFiSTiKChapter
---------------

The `SOFiSTiKChapter` eases the manipulation of a subset of SOFiSTiK programs in a
given SOFiSTiK chapter.

__author__ = "Studio W Engineers"

__version__ = "0.1.0"

__maintainer__ = "Studio W Engineers"

__email__ = "studio.w.engineers@gmail.com"

__status__ "Alpha"
"""
# standard library imports

# third party library imports

# local library specific imports
from .. _internals.program import SOFiSTiKProgram
from .. _internals.system_directive import SOFiSTiKSystemDirective


class SOFiSTiKChapter:
    """Auxiliary class that ease the manipulation of a subset of SOFiSTiK programs in a
    given SOFiSTiK chapter.
    """
    def __init__(self, name: str, is_active: bool = True) -> None:
        """The initializer of the `SOFiSTiKChapter` class.
        """
        self._is_active = is_active
        self._name = name.upper()
        self._directives: dict[str, SOFiSTiKSystemDirective] = {}
        self._order: list[str] = []
        self._programs: dict[str, SOFiSTiKProgram] = {}

    def __repr__(self) -> str:
        return f"SOFiSTiK chapter \"{self._name}\" with content:\n" + self.serialize()

    def add_directive(self, directive: SOFiSTiKSystemDirective) -> None:
        """Add a directive at the end of the chapter.
        """
        if not self.has_directive(directive.get_content_as_string()):
            self._directives.update({directive.get_content_as_string(): directive})
            self._order.append(directive.get_content_as_string())
            return

        err_msg = (f"Directive \"{directive.get_content_as_string()}\" already "
                   f"exists in chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def add_directive_after(
            self,
            directive: SOFiSTiKSystemDirective,
            target_name: str
        ) -> None:
        """Add a directive after `target_name`.
        """
        target_name = target_name.upper()
        try:
            index = self._order.index(target_name)

        except ValueError as exc:
            err_msg = f"\"{target_name}\" not found in chapter \"{self._name}\"!"
            raise ValueError(err_msg) from exc

        if not self.has_directive(directive.get_content_as_string()):
            self._directives.update({directive.get_content_as_string(): directive})
            self._order.insert(index + 1, directive.get_content_as_string())
            return

        err_msg = (f"Directive \"{directive.get_content_as_string()}\" already "
                   f"exists in chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def add_directive_before(
            self,
            directive: SOFiSTiKSystemDirective,
            target_name: str
        ) -> None:
        """Add a directive before `target_name`.
        """
        target_name = target_name.upper()
        try:
            index = self._order.index(target_name)

        except ValueError as exc:
            err_msg = f"\"{target_name}\" not found in chapter \"{self._name}\"!"
            raise ValueError(err_msg) from exc

        if not self.has_directive(directive.get_content_as_string()):
            self._directives.update({directive.get_content_as_string(): directive})
            self._order.insert(index, directive.get_content_as_string())
            return

        err_msg = (f"Directive \"{directive.get_content_as_string()}\" already "
                   f"exists in chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def add_program(self, new_program: SOFiSTiKProgram) -> None:
        """Add a program at the end of the chapter.
        """
        if not self.has_program(new_program.get_name()):
            self._programs.update({new_program.get_name(): new_program})
            self._order.append(new_program.get_name())
            return

        err_msg = (f"Program \"{new_program.get_name()}\" already exists in "
                   f"chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def add_program_after(self, new_program: SOFiSTiKProgram, target_name: str) -> None:
        """Add a program after `target_name`.
        """
        target_name = target_name.upper()
        try:
            index = self._order.index(target_name)

        except ValueError as exc:
            err_msg = f"\"{target_name}\" not found in chapter \"{self._name}\"!"
            raise ValueError(err_msg) from exc

        if not self.has_program(new_program.get_name()):
            self._programs.update({new_program.get_name(): new_program})
            self._order.insert(index + 1, new_program.get_name())
            return

        err_msg = (f"Program \"{new_program.get_name()}\" already exists in "
                   f"chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def add_program_before(self, new_program: SOFiSTiKProgram, target_name: str) -> None:
        """Add a program before `target_name`.
        """
        target_name = target_name.upper()
        try:
            index = self._order.index(target_name)

        except ValueError as exc:
            err_msg = f"\"{target_name}\" not found in chapter \"{self._name}\"!"
            raise ValueError(err_msg) from exc

        if not self.has_program(new_program.get_name()):
            self._programs.update({new_program.get_name(): new_program})
            self._order.insert(index, new_program.get_name())
            return

        err_msg = (f"Program \"{new_program.get_name()}\" already exists in "
                   f"chapter \"{self._name}\"!")
        raise RuntimeError(err_msg)

    def copy_program_to(self, source_program: str, target_program: str) -> None:
        """Copy the content of `source_program` to `target_program`. All the content of
        `target_program`, if any, will be overwritten except for its name.

        Parameters
        ----------
        source_program : str
            the name of the source program

        target_program : str
            the name of the target program

        Raises
        ------
        `RuntimeError`
            If `target_program` or `source_program` are not found.
        """
        if not self.has_program(source_program):
            err_msg = (f"Program \"{source_program.upper()}\" not found in chapter "
                       f"\"{self._name}\"!")
            raise RuntimeError(err_msg)

        if not self.has_program(target_program):
            err_msg = (f"Program \"{target_program.upper()}\" not found in chapter "
                       f"\"{self._name}\"!")
            raise RuntimeError(err_msg)

        # remove old content from the target program
        target_prog = self.get_program(target_program)
        target_prog.clear()

        source_prog = self.get_program(source_program)

        # copy the new content to target program
        for _ in source_prog.get_content():
            target_prog.add_row(_)

        # set name, type and active status to target program
        target_prog.set_name(target_program)
        target_prog.set_type(source_prog.get_type())
        if source_prog.is_active():
            target_prog.turn_on()
        else:
            target_prog.turn_off()

    def create_new_program(self,
                           name: str,
                           prog_type: str = "ASE",
                           is_active: bool = True
        ) -> None:
        """Create and add a new, empty program at the end of the chapter.
        """
        self.add_program(SOFiSTiKProgram.create_empty(name, prog_type, is_active))

    def create_new_program_after(self,
                                 program_to_search: str,
                                 name: str,
                                 prog_type: str = "ASE",
                                 is_active: bool = True
        ) -> None:
        """Create and add a new program in the current chapter and `dat` file.
        """
        self.add_program_after(
            SOFiSTiKProgram.create_empty(name, prog_type, is_active),
            program_to_search
        )

    def create_new_program_before(self,
                                 program_to_search: str,
                                 name: str,
                                 prog_type: str = "ASE",
                                 is_active: bool = True
        ) -> None:
        """Create and add a new program in the current chapter and `dat` file.
        """
        self.add_program_before(
            SOFiSTiKProgram.create_empty(name, prog_type, is_active),
            program_to_search
        )

    def get_directive(self, name: str) -> SOFiSTiKSystemDirective:
        """Return the system directive given its name.
        """
        name = name.upper()
        if self.has_directive(name):
            return self._directives[name]

        err_msg = f"Directive \"{name}\" not found in Chapter {self._name}!"
        raise RuntimeError(err_msg)

    def get_last_program(self) -> SOFiSTiKProgram:
        """Return the last program of this chapter.
        """
        if self._order:
            for index in range(len(self._order) - 1, 1, -1):
                if self.has_program(self._order[index]):
                    return self.get_program(self._order[index])

        raise RuntimeError(f"No programs found in chapter \"{self._name}\"!")

    def get_list_of_content(self) -> list[str]:
        """Return the list of contents in this chapter.
        """
        return self._order

    def get_name(self) -> str:
        """Return the name of this `SOFiSTiKChapter`."
        """
        return self._name

    def get_program(self, program_name: str) -> SOFiSTiKProgram:
        """Return the program given its name.
        """
        program_name = program_name.upper()
        if self.has_program(program_name):
            return self._programs[program_name]

        err_msg = f"Program \"{program_name}\" not found in Chapter {self._name}!"
        raise RuntimeError(err_msg)

    def get_program_index(self, program_name: str) -> int:
        """Return the program index given its name.
        """
        if self.has_program(program_name.upper()):
            return self._order.index(program_name.upper())

        err_msg = f"Program \"{program_name}\" not found in Chapter {self._name}!"
        raise RuntimeError(err_msg)

    def has_directive(self, directive_name: str) -> bool:
        """Check if this chapter has a directive with the given name.

        Returns
        -------
        `bool`
            `True` if `directive_name` is found, `False` otherwise.
        """
        return directive_name.upper() in self._directives

    def has_program(self, program_name: str) -> bool:
        """Check if this chapter has a program with the given name.

        Returns
        -------
        `bool`
            `True` if `program_name` is found, `False` otherwise.
        """
        return program_name.upper() in self._programs

    def remove_program(self, program_name: str) -> None:
        """Check if this chapter has a program with the given name and remove it.
        """
        program_name = program_name.upper()
        if self.has_program(program_name):
            del self._programs[program_name]
            self._order.remove(program_name)
            return

        err_msg = f"Program \"{program_name}\" not found in Chapter {self._name}!"
        raise RuntimeError(err_msg)

    def serialize(self) -> str:
        """Serialize the content of this `SOFiSTiKChapter` instance.
        """
        flag = "+" if self._is_active else "-"
        #NOTE: flag is a workaround for Python 3.11-, for 3.12+ can be done in one line
        output = f"!{flag}!CHAPTER " + self.get_name() + "\n\n"
        for name in self._order:
            try:
                output += self.get_program(name).serialize() + "\n\n"
            except RuntimeError:
                output += self.get_directive(name).serialize() + "\n\n"
        return output

    def turn_off(self) -> None:
        """Turn off all the programs and directives in the chapter.
        """
        self._is_active = False

        for program in self._programs.values():
            program.turn_off()

        for directive in self._directives.values():
            directive.turn_off()

    def turn_on(self) -> None:
        """Turn on all the programs and directives in the chapter.
        """
        self._is_active = True

        for program in self._programs.values():
            program.turn_on()

        for directive in self._directives.values():
            directive.turn_on()
