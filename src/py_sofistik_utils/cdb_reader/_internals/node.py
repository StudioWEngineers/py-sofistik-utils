# standard library imports

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . node_data import _NodeData
from . node_residual import _NodeResidual
from . node_result import _NodeResult
from . sofistik_dll import SofDll


class _Node:
    """
    The ``Nodes`` class is a wrapper that manages informations about nodes through
    member variables of classes ``NodeData``, ``NodeResiduals`` and ``NodeResults``.
    It provides easy abstractions for commonly used data manipulations, e.g, calculating
    nodal coordinates in deflected configuration.
    """

    data: _NodeData
    residuals: _NodeResidual
    results: _NodeResult

    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``Nodes`` class.
        """
        self.data = _NodeData(dll)
        self.residuals = _NodeResidual(dll)
        self.results = _NodeResult(dll)

        self._calculated_lc: set[int] = set()
        self._data = DataFrame(columns = ["LOAD_CASE", "ID", "X", "Y", "Z"])

    def calculate_deflected_configuration(self, load_case: int) -> None:
        """Calculate the nodal coordinates in deflected configuration for the given
        ``load_case``.
        """
        if not self.data.is_loaded():
            self.data.load()

        if not self.results.is_loaded(load_case):
            self.results.load(load_case)

        coord = self.data.get_all_coordinates()
        disp = self.results.get_all_displacements(load_case)

        for col in ["UX", "UY", "UZ"]:
            coord[col] = coord["ID"].map(disp.set_index("ID")[col]).fillna(0.0)

        for col in ["X", "Y", "Z"]:
            coord[col] = coord[f"{col}0"] + coord[f"U{col}"]

        coord.insert(loc=0, column="LOAD_CASE", value=load_case)
        coord = coord.drop(
            columns=["X0", "Y0", "Z0", "UX", "UY", "UZ"]
        ).reset_index(drop=True)

        self._calculated_lc.add(load_case)
        if self._data.empty:
            self._data = coord
        else:
            self._data = concat([self._data, coord], ignore_index=True)

    def clear(self, load_case: int) -> None:
        """Clear the results for the given ``load case``.
        """
        if not self.is_deflected_configuration_calculated(load_case):
            return

        self._data = self._data.drop(self._data[self._data.LOAD_CASE == load_case].index)
        self._calculated_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear the results for all the load cases.
        """
        if not self._calculated_lc:
            return

        self._data = self._data[0:0]
        self._calculated_lc.clear()

    def get_deflected_configuration(self, load_case: int) -> DataFrame:
        """Return the deformed configuration for the given ``load_case``.
        """
        if not self.is_deflected_configuration_calculated(load_case):
            raise LookupError(f"Load case {load_case} has not been calculated!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        return self._data.loc[lc_mask, ("ID", "X", "Y", "Z")].copy(deep=True)

    def is_deflected_configuration_calculated(self, load_case: int) -> bool:
        """Return ``True`` if the deflected configuration has been calculated for the
        given ``load_case``.
        """
        return load_case in self._calculated_lc
