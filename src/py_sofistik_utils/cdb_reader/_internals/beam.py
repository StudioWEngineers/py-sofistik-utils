# standard library imports

# third party library imports
from pandas import DataFrame

# local library specific imports
from . beam_data import _BeamData
from . beam_load import _BeamLoad
from . beam_results import BeamResults
from . beam_stresses import _BeamStress
from . property import _PropertyData
from . sofistik_dll import SofDll


class Beam:
    """
    The ``Beam`` class is a wrapper that manages informations about beams
    through member variables of classes ``_BeamData``, ``_BeamLoad``,
    ``_BeamResult`` and ``_BeamStresses``.
    It provides easy abstractions for commonly used data manipulations, e.g,
    calculating the strain energy.
    """

    data: _BeamData
    loads: _BeamLoad
    results: BeamResults
    stresses: _BeamStress

    def __init__(self, dll: SofDll) -> None:
        self.data = _BeamData(dll)
        self.loads = _BeamLoad(dll)
        self.results = BeamResults(dll)
        self.stresses = _BeamStress(dll)

        self._calculated_u_lc: set[int] = set()
        self._dll = dll
        self._u = DataFrame(
            columns=[
                "ELEM_ID",
                "GROUP",
                "LOAD_CASE",
                "U"
            ]
        )

    def calculate_strain_energy(self, load_cases: int | list[int]) -> None:
        """Calculate the strain energy for the given ``load_case`` numbers.

        Notes
        -----
        Please refer to the documentation for the hypotheses on which the
        calculation is based on.
        """
        if isinstance(load_cases, int):
            load_cases = [load_cases]
        else:
            load_cases = list(set(load_cases))

        if not self.data.is_loaded():
            self.data.load()

        # Load properties for all unique PROP_END_1/2
        prop_nmb = (
            set(self.data.data()["PROP_END_1"].unique()) |
            set(self.data.data()["PROP_END_2"].unique())
        )
        properties = _PropertyData(self._dll)
        for prop in prop_nmb:
            properties.load(int(prop))

        # Load results for all load cases
        self.results.load(load_cases)

        # Initialize base_data with zeros for required columns
        base_data = self.results.data().reset_index(drop=True)
        required_columns = ["LENGTH", "PROP_END_1", "PROP_END_2", "E", "A", "IYY", "IZZ", "U"]
        base_data[required_columns] = 0.0

        # Assign PROP_END_1/2 and LENGTH using vectorized operations
        elem_ids = base_data["ELEM_ID"].unique()
        base_data["PROP_END_1"] = base_data["ELEM_ID"].map({_: self.data.get(_, "PROP_END_1") for _ in elem_ids}).fillna(1).astype(int)
        base_data["PROP_END_2"] = base_data["ELEM_ID"].map({_: self.data.get(_, "PROP_END_2") for _ in elem_ids}).fillna(1).astype(int)
        base_data["LENGTH"] = base_data["ELEM_ID"].map({_: self.data.get(_) for _ in elem_ids}).fillna(1.0)

        for prop in prop_nmb:
            base_data.loc[base_data["PROP_END_1"] == prop, "A"] = properties.get_area(prop)
            base_data.loc[base_data["PROP_END_1"] == prop, "IYY"] = properties.get_second_moment_of_area_yy(prop)
            base_data.loc[base_data["PROP_END_1"] == prop, "IZZ"] = properties.get_second_moment_of_area_zz(prop)
            base_data.loc[base_data["PROP_END_2"] == prop, "A"] = properties.get_area(prop)
            base_data.loc[base_data["PROP_END_2"] == prop, "IYY"] = properties.get_second_moment_of_area_yy(prop)
            base_data.loc[base_data["PROP_END_2"] == prop, "IZZ"] = properties.get_second_moment_of_area_zz(prop)

        # Calculate strain energy (vectorized)
        E = 210000000  # kN/m²
        base_data["U"] = (1 / (2 * E)) * (
            base_data["N"] ** 2 / base_data["A"] +
            base_data["MY"] ** 2 / base_data["IYY"] +
            base_data["MZ"] ** 2 / base_data["IZZ"]
        )

        # Calculate segment lengths (next_POS - current_POS)
        base_data = base_data.sort_values(["LOAD_CASE", "ELEM_ID", "POS"])
        base_data["SEGMENT_LENGTH"] = base_data.groupby(["LOAD_CASE", "ELEM_ID"])["POS"].diff(-1).abs().fillna(0)

        # Calculate U for the next section (shifted U values)
        base_data["U_NEXT"] = base_data.groupby(["LOAD_CASE", "ELEM_ID"])["U"].shift(-1).fillna(0)

        # Calculate strain energy per segment: (U1 + U2) * L_seg / 2
        base_data["U_SEGMENT"] = (base_data["U"] + base_data["U_NEXT"]) * base_data["SEGMENT_LENGTH"] / 2

        # Sum strain energy across all segments for each (LOAD_CASE, ELEM_ID)
        result = base_data.groupby(["LOAD_CASE", "ELEM_ID"]).agg({
            "U_SEGMENT": "sum",
            "GROUP": "first"  # Assuming GROUP is the same for all segments of an ELEM_ID
        }).rename(columns={"U_SEGMENT": "U"}).reset_index()

        # Reorder columns to ['ELEM_ID', 'GROUP', 'LOAD_CASE', 'U']
        result = result[["ELEM_ID", "GROUP", "LOAD_CASE", "U"]]

        # Set multi-index for fast lookups
        self._u = result.set_index(
            ["LOAD_CASE", "ELEM_ID"],
            drop=False
        ).sort_index()

        self._calculated_u_lc.update(load_cases)

    def clear_strain_energy(self, load_case: int) -> None:
        """Clear the calculated strain energy for the given ``load_case``
        number.
        """
        if load_case not in self._calculated_u_lc:
            return

        self._data = self._u[
            self._u.index.get_level_values("LOAD_CASE") != load_case
        ]
        self._calculated_u_lc.remove(load_case)

    def clear_all_strain_energy(self) -> None:
        """Clear the calculated strain energy for all the load cases.
        """
        self._u = self._u[0:0]
        self._calculated_u_lc.clear()

    def get_element_strain_energy(
            self,
            load_case: int,
            element_id: int,
            default: float | None = None
    ) -> float:
        """Return the calculated strain energy for the given ``element_id`` and
        ``load_case``.
        """
        try:
            return self._u.at[(load_case, element_id), "U"]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Strain energy entry not found for element id {element_id} "
                f"and load case {load_case}!"
            ) from e

    def get_group_strain_energy(
            self,
            load_case: int,
            group: int,
            default: float | None = None
    ) -> float:
        """Return the sum of the calculated strain energy considering all the
        elements in the given ``group`` number and ``load_case``.
        """
        try:
            return self._u[self._u.GROUP == group].loc[load_case, "U"].sum()  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Strain energy could not be returned for group {group} "
                f"and load case {load_case}!"
            ) from e

    def get_strain_energy(self, deep: bool = True) -> DataFrame:
        """Return the calculated strain energy for all the loaded
        ``load_case``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._u.copy(deep=deep)
