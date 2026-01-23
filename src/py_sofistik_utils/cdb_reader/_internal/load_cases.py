"""
LoadCases
---------

The `LoadCases` class provides methods and data structure to:
    * access and load the keys `12/LC` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.

Not all the information provided by SOFiSTiK are stored and therefore made available. In
particular, the information loaded are:
    * Type of load case (key `KIND`);
    * Name of the load case (key `RTEX`);
    * SOFiSTiK source program (key `NAME`);
    * sum of the reaction forces (keys `RX`, `RY` and `RZ`);
    * laod case factors (keys `fact`, `factX`, `factY` and `factZ`);
    * PLC number (key `PLC`);
    * theory (key `THEO`);

For details, please refer to SOFiHELP - CDBase.
"""
# standard library imports
from ctypes import byref, cast, c_char_p, create_string_buffer, c_int, sizeof

# third party library imports
from numpy import array, float64, zeros
from numpy.typing import NDArray

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CLC_CTRL


class LoadCases:
    """The `LoadCases` class provides methods and data structure to:
    * access and load the keys `12/LC` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.

    Not all the information provided by SOFiSTiK are stored and therefore made available.
    In particular, the information loaded are:
    * Type of load case (key `KIND`);
    * Name of the load case (key `RTEX`);
    * SOFiSTiK source program (key `NAME`);
    * sum of the reaction forces (keys `RX`, `RY` and `RZ`);
    * laod case factors (keys `fact`, `factX`, `factY` and `factZ`);
    * PLC number (key `PLC`);
    * theory (key `THEO`);

        For details, please refer to SOFiHELP - CDBase.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `LoadCases` class.
        """
        self._dll = dll

        self._loaded_lc: set[int] = set()

        self._designation: dict[int, str] = {}
        self._factors: dict[int, NDArray[float64]] = {}
        self._kind: dict[int, str] = {}
        self._name: dict[int, str] = {}
        self._plc: dict[int, int] = {}
        self._reaction_sum: dict[int, NDArray[float64]] = {}
        self._theory: dict[int, str] = {}

    def clear(self, lc_nmb: int) -> None:
        """Clear the values for the given load case number.
        """
        if lc_nmb not in self._loaded_lc:
            raise RuntimeError(f"Load case {lc_nmb} not found!")

        del self._designation[lc_nmb]
        del self._factors[lc_nmb]
        del self._kind[lc_nmb]
        del self._name[lc_nmb]
        del self._plc[lc_nmb]
        del self._reaction_sum[lc_nmb]
        del self._theory[lc_nmb]

        self._loaded_lc.remove(lc_nmb)

    def clear_all(self) -> None:
        """Clear the values for all the load cases.
        """
        self._designation.clear()
        self._factors.clear()
        self._kind.clear()
        self._name.clear()
        self._plc.clear()
        self._reaction_sum.clear()
        self._theory.clear()

        self._loaded_lc.clear()

    def get_designation(self, load_case: int) -> str:
        """Return the designation for the given `load_case`. An empty string is returned
        if the `load_case` is not found.
        """
        return self._designation.get(load_case, "")

    def get_factors(self, load_case: int) -> NDArray[float64]:
        """Return the factors of the given `load_case`. A zero vector is returned if the
        `load_case` is not found.
        """
        return self._factors.get(load_case, zeros(4, dtype = float64))

    def get_kind(self, load_case: int) -> str:
        """Return the kind of the given `load_case`. An empty string is returned if the
        `load_case` is not found.
        """
        return self._kind.get(load_case, "")

    def get_name(self, load_case: int) -> str:
        """Return the name of the given `load_case`. An empty string is returned
        if the `load_case` is not found.
        """
        return self._name.get(load_case, "")

    def get_plc(self, load_case: int) -> int:
        """Return the number of the PLC for the given `load_case`. `-1` is returned if the
        `load_case` is not found.
        """
        return self._plc.get(load_case, -1)

    def get_reactions(self, load_case: int) -> NDArray[float64]:
        """Return the sum of the reaction forces for the given `load_case`. A zero vector
        is returned if the `load_case` is not found.
        """
        return self._reaction_sum.get(load_case, zeros(4, dtype = float64))

    def get_theory(self, load_case: int) -> str:
        """Return the theory for the given `load_case`. An empty string is returned
        if the the `load_case` is not found.
        """
        return self._theory.get(load_case, "")

    def load(self, lc_nmb: int) -> None:
        """Load information for given load cases (key `12/lc_nmb`).
        """
        if self._dll.key_exist(12, lc_nmb):
            lc = CLC_CTRL()
            rec_length = c_int(sizeof(lc))
            return_value = c_int(0)

            name = create_string_buffer(17 * 4 + 1)

            if lc_nmb in self._loaded_lc:
                self.clear(lc_nmb)

            return_value.value = self._dll.get(
                1,
                12,
                lc_nmb,
                byref(lc),
                byref(rec_length),
                0
            )

            self._dll.to_string(byref(lc.m_rtex),
                                byref(name),
                                sizeof(name))

            match lc.m_kind:
                case 0:
                    kind = "LINEAR LOAD CASE"
                case 1:
                    kind = "NON-LINEAR LOAD CASE"
                case 2:
                    kind = "SUPERPOSITION LOAD CASE"
                case 3:
                    kind = "INFLUENCE LINE"
                case 4:
                    kind = "DYNAMIC EIGENMODE"
                case 5:
                    kind = "BUCKLING MODE"
                case 6:
                    kind = "DESIGN CASE"
                case 7:
                    kind = "TRAIN LOAD DEFINITION"
                case 8:
                    kind = "TRANSIENT FUNCTION"
                case _:
                    kind = "ILLEGAL LOAD CASE"

            match lc.m_theo:
                case 0:
                    theory = "1ST ORDER THEORY"
                case 1:
                    theory = "2ND ORDER THEORY"
                case 2:
                    theory = "TOTAL LAGRANGIAN"
                case 3:
                    theory = "UPDATED LAGRANGIAN"
                case _:
                    err_msg = f"Unknown error in theory of load case {lc_nmb}"
                    raise RuntimeError(err_msg)

            # dirty fix
            temp_values = (c_int * 5)(*[lc.m_name[_] for _ in range(0, 5)])
            temp_cast = cast(temp_values, c_char_p).value.decode("latin-1").rstrip().split(" ")  # type: ignore[union-attr]
            designation = "".join(_ + " " for _ in temp_cast[:2]).rstrip()
            self._designation[lc_nmb] = designation

            self._factors[lc_nmb] = array(
                [lc.m_fact, lc.m_facx, lc.m_facy, lc.m_facz], dtype = float64
            )
            self._kind[lc_nmb] = kind
            self._name[lc_nmb] = name.value.decode()
            self._plc[lc_nmb] = lc.m_plc
            self._reaction_sum[lc_nmb] = array(
                [lc.m_rx, lc.m_ry, lc.m_rz], dtype = float64
            )
            self._theory[lc_nmb] = theory

            self._loaded_lc.add(lc_nmb)

    def load_all(self) -> None:
        """Load information for all the load cases (keys `12/LC`).
        """
        for lc_nmb in range(1, 99999):
            self.load(lc_nmb)
