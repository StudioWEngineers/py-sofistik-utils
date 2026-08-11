# standard library imports
from ctypes import byref, cast, c_char_p, create_string_buffer, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CLC_CTRL


class LoadCase:
    """This class provides methods and a data structure to:

        * access keys ``12/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``LOAD_CASE``: load case number
        * ``TYPE``: type of load case
        * ``NAME``: designation of loadcase
        * ``SOURCE``: name of program and program version separated by a blank
            program version has the form <Major>-<Service-Pack>.<Patch>.<Build>
        * ``RX``: sum of support reactions (X-component) [kN]
        * ``RY``: sum of support reactions (Y-component) [kN]
        * ``RZ``: sum of support reactions (Z-component) [kN]
        * ``PLC``: primary load case number [-]
        * ``THEORY``: the "TH3" parameter as set in ASE

        The ``DataFrame`` uses a MultiIndex with level ``LOAD_CASE`` to enable
        fast lookups via the `get` method. The index columns are not dropped
        from the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored:

            * construction stage number of birth and death
            * dead load factors (X, Y and Z)
            * access number
            * ...

            Please refer to the SOFiSTiK CDBHelp for a comprehensive list. This
            is a deliberate design choice and may be changed in the future
            without breaking the existing API.
    """
    _THEORY = {
        0: "1ST ORDER",
        1: "2ND ORDER",
        2: "TOTAL LAGRANGIAN",
        3: "UPDATED LAGRANGIAN"
    }

    _TYPE = {
        0: "LINEAR",
        1: "NON-LINEAR",
        2: "SUPERPOSITION",
        3: "INFLUENCE LINE",
        4: "DYNAMIC EIGENMODE",
        5: "BUCKLING MODE",
        6: "DESIGN CASE",
        7: "TRAIN LOAD DEFINITION",
        8: "TRANSIENT FUNCTION"
    }

    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "TYPE",
                "NAME",
                "SOURCE",
                "RX",
                "RY",
                "RZ",
                "PLC",
                "THEORY"
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

    def get(
            self,
            load_case: int,
            quantity: str,
            default: float | None = None
    ) -> float:
        """Retrieve the requested load case data.

        Parameters
        ----------
        load_case : int
            Load case number
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``"TYPE"``
            - ``"NAME"``
            - ``"SOURCE"``
            - ``"RX"``
            - ``"RY"``
            - ``"RZ"``
            - ``"PLC"``
            - ``"THEORY"``

        default : float or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float
            The requested value if found. If not found, returns ``default``
            when it is not None.

        Raises
        ------
        LookupError
            If the requested result is not found and ``default`` is None.
        """
        try:
            return self._data.at[load_case, quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Load case entry not found for load case {load_case} "
                f"and quantity {quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys
        ``12/LC``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve load case data for the given ``load_cases``. If a load
        case is not found, a warning is raised only if ``echo_level > 0``.

        Parameters
        ----------
        load_cases : int | list[int]
            load case numbers
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]
        else:
            load_cases = list(set(load_cases))  # remove duplicated entries

        # load data
        data: list[dict[str, float | int | str]] = []
        for load_case in load_cases:
            if self._dll.key_exist(12, load_case):
                self.clear(load_case)
                data.extend(self._load(load_case))
            else:
                if self._echo_level > 0:
                    print(f"Load case data not found for LC = {load_case}!")

        # set indices for fast lookup
        df = DataFrame(
            data
        ).sort_values("LOAD_CASE", kind="mergesort").set_index("LOAD_CASE")

        # merge data
        if self._data.empty:
            self._data = df
        else:
            self._data = concat([self._data, df])
            self._data.sort_index(inplace=True)
        self._loaded_lc.update(load_cases)

    def load_all(self) -> None:
        """Retrieve load case data for load cases 1 to 99999.
        """
        echo_level = self._echo_level
        self.set_echo_level(0)
        self.load(list(range(1, 100000, 1)))
        self.set_echo_level(echo_level)

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.

        Parameters
        ----------
        echo_level : int
            the new echo level
        """
        self._echo_level = echo_level

    def _load(self, load_case: int) -> list[dict[str, float | int | str]]:
        """Retrieve key ``12/load_case`` using SOFiSTiK dll.
        """
        lc = CLC_CTRL()
        rec_length = c_int(sizeof(lc))
        return_value = c_int(0)

        data: list[dict[str, float | int | str]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                12,
                load_case,
                byref(lc),
                byref(rec_length),
                0 if first_call else 1
            )

            rec_length = c_int(sizeof(lc))
            first_call = False
            if return_value.value >= 2:
                break

            name = create_string_buffer(17 * 4 + 1)
            self._dll.to_string(byref(lc.m_rtex), byref(name), sizeof(name))

            source = " ".join(
                (
                    cast(
                        (c_int * 5)(*lc.m_name[:5]),
                        c_char_p
                    ).value or b""
                ).decode("latin-1").split()[:2]
            )

            data.append(
                {
                    "LOAD_CASE": load_case,
                    "TYPE": self._TYPE.get(lc.m_kind, "ILLEGAL LOAD CASE"),
                    "NAME": name.value.decode(),
                    "SOURCE": source,
                    "RX": lc.m_rx,
                    "RY": lc.m_ry,
                    "RZ": lc.m_rz,
                    "PLC": lc.m_plc,
                    "THEORY": self._THEORY.get(lc.m_theo, "UNKNOWN")
                }
            )

        return data
