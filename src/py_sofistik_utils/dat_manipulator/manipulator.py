"""
SOFiSTiKDATManipulator
----------------------

The `SOFiSTiKDATManipulator` class load, create, modifiy and save `dat` files to be
used within the commercial SOFiSTiK finite element analysis package.

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
from . _internals.chapter import SOFiSTiKChapter
from . _internals.program import SOFiSTiKProgram
from . _internals.system_directive import is_system_directive, SOFiSTiKSystemDirective


class SOFiSTiKDATManipulator:
    """The `SOFiSTiKDATManipulator` class loads, creates, modifies and saves `dat` files
    to be used within the commercial SOFiSTiK finite element analysis package.
    """
    def __init__(self, file_name: str, path_to_folder: str) -> None:
        """The initializer of the `SOFiSTiKDATManipulator` class.
        """
        self._echo_level: int = 0
        self._full_name: str = path_to_folder + file_name + ".dat"
        self._original_content: list[str] = []

        self._chapters: dict[str, SOFiSTiKChapter] = {}
        self._directives: dict[str, SOFiSTiKSystemDirective] = {}
        self._order: list[str] = []
        self._programs: dict[str, SOFiSTiKProgram] = {}

    def __repr__(self) -> str:
        return f"SOFiSTiK file \"{self._full_name}\" with content:\n" + self.serialize()

    def add_chapter(self, chapter_name: str) -> None:
        """Add a new, empty chapter at the end of this `dat` file.
        """
        chapter_name = chapter_name.upper()
        if not self.has_chapter(chapter_name):
            self._chapters.update({chapter_name: SOFiSTiKChapter(chapter_name)})
            self._order.append(chapter_name)
            return

        err_msg = f"Chapter \"{chapter_name}\" already exists in \"{self._full_name}\"!"
        raise RuntimeError(err_msg)

    def add_directive(self, directive: SOFiSTiKSystemDirective) -> None:
        """Add a directive at the end of the file.
        """
        if not self.has_directive(directive.get_content_as_string()):
            self._directives.update({directive.get_content_as_string(): directive})
            self._order.append(directive.get_content_as_string())
            return

        err_msg = f"Directive \"{directive.get_content_as_string()}\" already exists!"
        raise RuntimeError(err_msg)

    def add_program(self, program: SOFiSTiKProgram) -> None:
        """Add an existing program to this `dat` file.
        """
        if not self.has_program(program.get_name()):
            self._programs.update({program.get_name(): program})
            self._order.append(program.get_name())
            return

        err_msg = (f"Program \"{program.get_name()}\" already exists in "
                   f" \"{self._full_name}\"!")
        raise RuntimeError(err_msg)

    def create_new_program(self,
                           name: str,
                           prog_type: str = "ASE",
                           is_active: bool = True
        ) -> None:
        """Create and add a new program in the current `dat` file.

        Raises
        ------
        `RuntimeError`
            If there is already a program with the given name.
        """
        self.add_program(SOFiSTiKProgram.create_empty(name, prog_type, is_active))

    def get_chapter(self, chapter_name: str) -> SOFiSTiKChapter:
        """Return the chapter given its name.

        Raises
        ------
        `RuntimeError`
            If `chapter_name` is not found.
        """
        chapter_name = chapter_name.upper()
        if self.has_chapter(chapter_name):
            return self._chapters[chapter_name]

        err_msg = f"Chapter \"{chapter_name}\" not found in {self._full_name}!"
        raise RuntimeError(err_msg)

    def get_directive(self, name: str) -> SOFiSTiKSystemDirective:
        """Return the system directive given its name.
        """
        name = name.upper()
        if self.has_directive(name):
            return self._directives[name]

        raise RuntimeError(f"Directive \"{name}\" not found!")

    def get_echo_level(self) -> int:
        """Return the `echo_level` of this instance of `SOFiSTiKDATManipulator`.
        """
        return self._echo_level

    def get_list_of_content(self) -> list[str]:
        """Return the list of contents of this `SOFiSTiKDATManipulator` instance.
        """
        return self._order

    def get_original_content(self) -> list[str]:
        """Return the original content of this `SOFiSTiKDATManipulator` instance, without
        any modifications.
        """
        return self._original_content

    def get_program(self, program_name: str) -> SOFiSTiKProgram:
        """Return the program given its name.

        Raises
        ------
        `RuntimeError`
            If `program_name` is not found.
        """
        if self.has_program(program_name.upper()):
            return self._programs[program_name.upper()]

        err_msg = f"Program \"{program_name}\" not found in {self._full_name}!"
        raise RuntimeError(err_msg)

    def get_program_index(self, program_name: str) -> int:
        """Return the program index given its name.
        """
        if self.has_program(program_name.upper()):
            return self._order.index(program_name.upper())

        err_msg = f"Program \"{program_name}\" not found in file {self._full_name}.dat!"
        raise RuntimeError(err_msg)

    def has_chapter(self, chapter_name: str) -> bool:
        """Check if this dat file has a chapter with the given name.

        Returns
        -------
        `bool`
            `True` if `chapter_name` is found, `False` otherwise.
        """
        return chapter_name.upper() in self._chapters

    def has_directive(self, directive_name: str) -> bool:
        """Check if this file has a directive with the given name.

        Returns
        -------
        `bool`
            `True` if `directive_name` is found, `False` otherwise.
        """
        return directive_name.upper() in self._directives

    def has_program(self, program_name: str) -> bool:
        """Check if this dat file has a program with the given name.

        Returns
        -------
        `bool`
            `True` if `program_name` is found, `False` otherwise.
        """
        return program_name.upper() in self._programs

    def initialize(self) -> None:
        """Load the `.dat` file associated to this instance of the
        `SOFiSTiKDATManipulator` class and store its content in uppercase format and
        without trailing whitespaces.

        A copy of the original content is kept in `_original_content`, without trailing
        whitespaces.
        """
        with open(self._full_name, "r", encoding="utf-8") as input_file:
            for line in input_file:
                self._original_content.append(line.rstrip())

        self._build_structure()

    def load_external_text_file(self,
                                folder: str,
                                file_name: str,
                                extension: str
        ) -> list[MutableString]:
        """Load an external text file and return its content in uppercase format and
        without trailing whitespaces.

        Parameters
        ----------
        folder : str
        file_name : str
        extension : str

        Returns
        -------
        list[MutableString]
            The content of the text file as a list of `MutableString`s.
        """
        full_name = folder + file_name + "." + extension
        with open(full_name, "r", encoding="utf-8") as input_file:
            content = input_file.readlines()

        return_list = []
        for line in content:
            return_list.append(MutableString(line.rstrip().upper()))

        return return_list

    def save(self) -> None:
        """Override the original `dat` file.
        """
        with open(self._full_name, "w", encoding="utf-8") as out_file:
            out_file.write(self.serialize())

    def save_as(self,
                path_to_folder: str,
                file_name: str ,
                extension: str = "dat"
        ) -> None:
        """Save the actual content of this `dat` file to the given file.
        """
        full_name = path_to_folder + file_name + "." + extension

        with open(full_name, "w", encoding="utf-8") as out_file:
            out_file.write(self.serialize())

    def save_original_as(self,
                         path_to_folder: str,
                         file_name: str ,
                         extension: str = "dat"
        ) -> None:
        """Save the content of the original, unmodified `.dat` file to the given file.
        """
        full_name = path_to_folder + file_name + "." + extension

        with open(full_name, "w", encoding="utf-8") as out_file:
            for row in self._original_content:
                out_file.write(row + "\n")

    def serialize(self) -> str:
        """Serialize the content of this `SOFiSTiKDATManipulator` instance.
        """
        output = ""
        for item in self._order:
            if self.has_program(item):
                output += self.get_program(item).serialize() + "\n\n"
            elif self.has_chapter(item):
                output += self.get_chapter(item).serialize()
            else:
                output += self.get_directive(item).serialize() + "\n\n"

        return output

    def set_echo_level(self, new_echo_level: int) -> None:
        """Set the `echo_level` for this instance of `SOFiSTiKDATManipulator`.
        """
        self._echo_level = new_echo_level

    def turn_on(self) -> None:
        """Turn on all the chapters and programs.
        """
        for chapter in self._chapters.values():
            chapter.turn_on()

        for program in self._programs.values():
            program.turn_on()

        for directive in self._directives.values():
            directive.turn_on()

    def turn_off(self) -> None:
        """Turn off all the programs in this file.
        """
        for chapter in self._chapters.values():
            chapter.turn_off()

        for program in self._programs.values():
            program.turn_off()

        for directive in self._directives.values():
            directive.turn_off()

    def _build_structure(self) -> None:
        """Identify SOFiSTiK programs and create `SOFiSTiKProgram` instances accordingly.
        """
        temp = [_.rstrip().upper() for _ in self._original_content]
        chapters = self._count_chapters(temp)
        directives = self._count_directives(temp)
        programs = self._count_programs(temp)
        order = self._get_order(programs, chapters, directives)

        if temp[0].lstrip()[1:5].upper() != "PROG":
            raise RuntimeError("In this context SOFiSTiK dat files must start with PROG!")

        # create programs and chapters
        chapter = None
        for item in order:
            if chapters is not None:
                if item in chapters:
                    c_state = temp[item[0]].split()[0][1] == "+"
                    c_name = "".join(_ + " " for _ in temp[item[0]].split()[1:]).rstrip()
                    chapter = SOFiSTiKChapter(c_name, c_state)
                    self._chapters.update({c_name: chapter})
                    self._order.append(c_name)
            if item in programs:
                p_name = temp[item[0] + 1].lstrip()[5:]
                content = [MutableString(temp[_]) for _ in range(item[0], item[1] + 1)]
                program = SOFiSTiKProgram(deepcopy(content), p_name)

                if chapter is not None:
                    chapter.add_program(program)
                else:
                    self._programs.update({p_name: program})
                    self._order.append(p_name)

            if directives is not None:
                if item in directives:
                    direc = SOFiSTiKSystemDirective.from_string(temp[item[0]])
                    if chapter is not None:
                        chapter.add_directive(direc)
                    else:
                        self._directives.update({direc.get_content_as_string(): direc})
                        self._order.append(direc.get_content_as_string())

    @staticmethod
    def _count_chapters(content: list[str]) -> list[tuple[int, int]] | None:
        """Return a list of tuples each one containing the start and end line of a
        chapter. If no chapters have been defined, return `None`.
        """
        indexes: list[int] = []
        there_is_chapter = False
        for line_index, line in enumerate(content):
            if line.lstrip()[3:10] == "CHAPTER":
                indexes.append(line_index)
                if there_is_chapter:
                    indexes.append(line_index - 1)
                there_is_chapter = True

        if there_is_chapter:
            indexes.append(len(content))
            indexes.sort()
            return [(indexes[_], indexes[_ + 1]) for _ in range(0, len(indexes), 2)]

        return None

    @staticmethod
    def _count_directives(content: list[str]) -> list[tuple[int, int]] | None:
        """Return a list of tuples each one containing the start and end line of a
        directive. If no directives have been defined, return `None`.
        """
        indexes = []
        for line_index, line in enumerate(content):
            if is_system_directive(line):
                indexes.append(line_index)

        if indexes:
            return [(indexes[_], indexes[_]) for _ in range(0, len(indexes))]
        return None

    @staticmethod
    def _count_programs(content: list[str]) -> list[tuple[int, int]]:
        """Return a list of tuples each one containing the start and end line of a
        program.

        It is assumed that a program can have maximum two END statement within its body.
        The first one either close an LC block (in case it is looped ASE) or can be the
        end, while the second must be the end of the program.
        """
        indexes = []
        end_found = False
        for line_index, line in enumerate(content):
            if line.lstrip()[1:5] == "PROG":
                indexes.append(line_index)
                end_found = False
            try:
                if line.lstrip().split(" ")[0] == "END":
                    # assume first END is the one that closes the program
                    if not end_found:
                        indexes.append(line_index)

                    # but if another END is found then the first one is replaced
                    else:
                        del indexes[-1]
                        indexes.append(line_index)
                    end_found = True

            except IndexError:
                pass

        return [(indexes[_], indexes[_ + 1]) for _ in range(0, len(indexes), 2)]

    @staticmethod
    def _get_order(
        programs: list[tuple[int, int]],
        chapters: list[tuple[int, int]] | None,
        directives: list[tuple[int, int]] | None
    ) -> list[tuple[int, int]]:
        """Return and ordered list of programs, chapters and directives, as defined in
        Teddy.
        """
        order = deepcopy(programs)
        if chapters is not None:
            order += chapters
        if directives is not None:
            order += directives
        order.sort(key=lambda _: _[0])

        return order
