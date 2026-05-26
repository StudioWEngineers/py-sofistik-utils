# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . beam_data import _BeamData
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CBEAM_FOR


class BeamResults:
    """
    This class provides methods and a data structure to:

    * access keys ``102/LC`` of the CDB file;
    * store the retrieved data in a convenient format;
    * provide access to the data after the CDB is closed.

    The underlying data structure is a :class:`pandas.DataFrame` with the
    following columns:

    * ```LOAD_CASE```: the load case number
    * ``GROUP``: the beam group number
    * ``ELEM_ID``: the beam number
    * ``POS``: position of the output station along the beam [m]
    * ``POS_REL``: relative position of the output station along the beam
      (0 to 1)
    * ``N``: axial force [kN]
    * ``VY``: shear force Y [kN]
    * ``VZ``: shear force Z [kN]
    * ``MT``: torsional moment [kNm]
    * ``MY``: bending moment around Y [kNm]
    * ``MZ``: bending moment around Z [kNm]
    * ``MB``: warping moment [kNm]
    * ``MT2``: second torsional moment [kNm]

    The ``DataFrame`` uses a MultiIndex with levels ``ELEM_ID``, ``LOAD_CASE``
    and ``STATION`` (in this specific order) to enable fast lookups via the
    `get` method. The index columns are not dropped from the ``DataFrame``.

    .. note::

        Not all available quantities are retrieved and stored. In
        particular:

        * displacements and rotations in local coordinates
        * twist angle
        * 3rd torsional moment
        * axial and transverse beddings
        * local y and z components of the transverse beddings

        are currently not included. This is a deliberate design choice and
        may be changed in the future without breaking the existing API.

    .. important::

        The relative output station ``POS_REL`` is rounded to two decimal
        places to prevent floating-point errors for lookups at the beam end
        (``POS_REL = 1.0``) or at any other intermediate station.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "POS",
                "POS_REL",
                "N",
                "VY",
                "VZ",
                "MT",
                "MY",
                "MZ",
                "MB",
                "MT2"
            ]
        )
        self._dll = dll
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
            element_id: int,
            load_case: int,
            position: float,
            quantity: str,
            default: float | None = None
    ) -> float:
        """Retrieve the requested beam result.

        Parameters
        ----------
        element_id : int
            Beam element number
        load_case : int
            Load case number
        position : float
            Relative position of the output station along the beam (0 to 1)
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``N``
            - ``VY``
            - ``VZ``
            - ``MT``
            - ``MY``
            - ``MZ``
            - ``MB``
            - ``MT2``

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
            return self._data.at[
                (element_id, load_case, position),
                quantity
            ]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Beam result entry not found for element id {element_id}, "
                f"load case {load_case}, position {position} and quantity "
                f"{quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys
        ``102/LC``.

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
        """Retrieve beam results for the given ``load_cases``. If a load case
        is not found, a warning is raised only if ``echo_level > 0``.

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
        data: list[dict[str, float | int]] = []
        for load_case in load_cases:
            if self._dll.key_exist(102, load_case):
                self.clear(load_case)
                data.extend(self._load(load_case))

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        df = DataFrame(data).sort_values("ELEM_ID", kind="mergesort")
        elem_ids = df["ELEM_ID"]

        for grp, grp_range in group_data.iterator("BEAM"):
            if grp_range.stop == 0:
                continue
            left = elem_ids.searchsorted(grp_range.start, side="left")
            right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
            df.loc[df.index[left:right], "GROUP"] = grp

        # calculating adimensional length
        beam_data = _BeamData(self._dll)
        beam_data.load()
        elem_to_factor = {
            _: beam_data.get(_, "LENGTH") for _ in df["ELEM_ID"].unique()
        }
        factors = df["ELEM_ID"].map(elem_to_factor).fillna(1.0).astype(float)
        df["POS_REL"] = (df["POS_REL"] / factors).round(2)

        # set indices for fast lookup
        df = df.set_index(["ELEM_ID", "LOAD_CASE", "POS_REL"], drop=False)

        # merge data
        if self._data.empty:
            self._data = df
        else:
            self._data = concat([self._data, df])
        self._loaded_lc.update(load_cases)

    def _load(self, load_case: int) -> list[dict[str, float | int]]:
        """Retrieve key ``102/load_case`` using SOFiSTiK dll.
        """
        beam_res = CBEAM_FOR()
        record_length = c_int(sizeof(beam_res))
        return_value = c_int(0)

        data: list[dict[str, float | int]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                102,
                load_case,
                byref(beam_res),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(beam_res))
            first_call = False
            if return_value.value >= 2:
                break

            if beam_res.m_nr > 0:
                data.append(
                    {
                        "LOAD_CASE": load_case,
                        "GROUP": 0,
                        "ELEM_ID": beam_res.m_nr,
                        "POS": beam_res.m_x,
                        "POS_REL": beam_res.m_x,
                        "N": beam_res.m_n,
                        "VY": beam_res.m_vy,
                        "VZ": beam_res.m_vz,
                        "MT": beam_res.m_mt,
                        "MY": beam_res.m_my,
                        "MZ": beam_res.m_mz,
                        "MB": beam_res.m_mb,
                        "MT2": beam_res.m_mt2
                    }
                )

        return data
