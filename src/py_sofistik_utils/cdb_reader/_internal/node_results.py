"""
NodeResults
-----------

The `NodeResults` class provides abstractions to load and access information about the
nodal results, contained in keys `24/LC` of the CDB file.

Data are stored in a `pandas` `DataFrame` having the following columns:

    * `LOAD_CASE`: load combination number
    * `ID`: node number
    * `UX`: X component of the nodal displacement (translation)
    * `UY`: Y component of the nodal displacement (translation)
    * `UZ`: Z component of the nodal displacement (translation)
    * `URX`: X component of the nodal displacement (rotation)
    * `URY`: Y component of the nodal displacement (rotation)
    * `URZ`: Z component of the nodal displacement (rotation)
    * `URB`: twist rotation
    * `PX`: X component of the nodal reaction (translation)
    * `PY`: Y component of the nodal reaction (translation)
    * `PZ`: Z component of the nodal reaction (translation)
    * `MX`: X component of the nodal reaction (rotation)
    * `MY`: Y component of the nodal reaction (rotation)
    * `MZ`: Z component of the nodal reaction (rotation)
    * `MB`: warping moment
"""
# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CN_DISP


class NodeResults:
    """The `NodeResults` class provides abstractions to load and access information
        about the nodal results, contained in keys `24/LC` of the CDB file.

        Data are stored in a `pandas` `DataFrame` having the following columns:

        * `LOAD_CASE`: load combination number
        * `ID`: node number
        * `UX`: X component of the nodal displacement (translation)
        * `UY`: Y component of the nodal displacement (translation)
        * `UZ`: Z component of the nodal displacement (translation)
        * `URX`: X component of the nodal displacement (rotation)
        * `URY`: Y component of the nodal displacement (rotation)
        * `URZ`: Z component of the nodal displacement (rotation)
        * `URB`: twist rotation
        * `PX`: X component of the nodal reaction (translation)
        * `PY`: Y component of the nodal reaction (translation)
        * `PZ`: Z component of the nodal reaction (translation)
        * `MX`: X component of the nodal reaction (rotation)
        * `MY`: Y component of the nodal reaction (rotation)
        * `MZ`: Z component of the nodal reaction (rotation)
        * `MB`: warping moment
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `NodeResults` class.
        """
        self._data: DataFrame = DataFrame(
            columns = [
                "LOAD_CASE",
                "ID",
                "UX",
                "UY",
                "UZ",
                "URX",
                "URY",
                "URZ",
                "URB",
                "PX",
                "PY",
                "PZ",
                "MX",
                "MY",
                "MZ",
                "MB"
            ]
        )
        self._dll = dll
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the results for the given `load case`.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.drop(self._data[self._data.LOAD_CASE == load_case].index)
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear the results for all the load cases.
        """
        if not self._loaded_lc:
            return

        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_all_displacements(self, load_case: int) -> DataFrame:
        """Return all of the nodal translational components of the displacements for the
        given `load_case`.

        Parameters
        ----------
        `load_case`: int
            Load case number

        Raises
        ------
        LookupError
            If the given `load_case` is not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        return self._data.loc[lc_mask, ("ID", "UX", "UY", "UZ")].copy(deep=True)  # type: ignore

    def get_displacements(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal translational components of the displacements for the given
        `load_case` and `node_number`.

        Parameters
        ----------
        `load_case`: int
            Load case number
        `node_number`: int
            Node number

        Raises
        ------
        LookupError
            If the given `load_case` or `node_nmb` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (lc_mask & id_mask).eq(False).all():
            err_msg = f"Node {node_number} not found in load case {load_case}!"
            raise LookupError(err_msg)

        return self._data.loc[lc_mask & id_mask, ("UX", "UY", "UZ")].copy(deep=True)  # type: ignore

    def get_reaction_forces(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal translational components of the reaction forces for the given
        `load_case` and `node_number`.

        Parameters
        ----------
        `load_case`: int
            Load case number
        `node_number`: int
            Node number

        Raises
        ------
        LookupError
            If the given `load_case` or `node_number` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            err_msg = f"Node {node_number} not found in load case {load_case}!"
            raise LookupError(err_msg)

        return self._data.loc[lc_mask & id_mask, ("PX", "PY", "PZ")].copy(deep=True)  # type: ignore

    def get_reaction_moments(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal rotational components of the reaction forces for the given
        `load_case` and `node_number`.

        Parameters
        ----------
        `load_case`: int
            Load case number
        `node_number`: int
            Node number

        Raises
        ------
        LookupError
            If the given `load_case` or `node_number` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            err_msg = f"Node {node_number} not found in load case {load_case}!"
            raise LookupError(err_msg)

        return self._data.loc[lc_mask & id_mask, ("MX", "MY", "MZ", "MB")].copy(deep=True)  # type: ignore

    def get_rotations(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal rotational components of the displacements for the given
        `load_case` and `node_number`.

        Parameters
        ----------
        `load_case`: int
            Load case number
        `node_number`: int
            Node number

        Raises
        ------
        LookupError
            If the given `load_case` or `node_number` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            err_msg = f"Node {node_number} not found in load case {load_case}!"
            raise LookupError(err_msg)

        return self._data.loc[lc_mask & id_mask, ("URX", "URY", "URZ", "URB")].copy(deep=True)  # type: ignore

    def get_values(self, load_case: int) -> DataFrame:
        """Return the results for the given `load_case`.

        Parameters
        ----------
        `load_case`: int
            Load case number

        Raises
        ------
        LookupError
            If the given `load_case` is not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        return self._data.loc[lc_mask].copy(deep=True)

    def is_loaded(self, load_case: int) -> bool:
        """Return `True` if the results have been loaded for the given `load_case`.
        """
        return load_case in self._loaded_lc

    def load(self, load_case: int) -> None:
        """Load the nodal results for the given `load_case`.
        """
        if self._dll.key_exist(24, load_case):
            node = CN_DISP()
            rec_length = c_int(sizeof(node))
            return_value = c_int(0)

            self.clear(load_case)

            temp_container: list[dict[str, Any]] = []
            count = 0
            while return_value.value < 2:
                node = CN_DISP()
                return_value.value = self._dll.get(
                    1,
                    24,
                    load_case,
                    byref(node),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                rec_length = c_int(sizeof(node))
                count += 1

                if return_value.value >= 2:
                    break

                temp_container.append(
                    {
                        "LOAD_CASE":load_case,
                        "ID": node.m_nr,
                        "UX": node.m_ux,
                        "UY": node.m_uy,
                        "UZ": node.m_uz,
                        "URX": node.m_urx,
                        "URY": node.m_ury,
                        "URZ": node.m_urz,
                        "URB": node.m_urb,
                        "PX": node.m_px,
                        "PY": node.m_py,
                        "PZ": node.m_pz,
                        "MX": node.m_mx,
                        "MY": node.m_my,
                        "MZ": node.m_mz,
                        "MB": node.m_mb
                    }
                )

            # remove max min
            del temp_container[0:2]

            if self._data.empty:
                self._data = DataFrame(temp_container)
            else:
                self._data = concat(
                    [self._data, DataFrame(temp_container)],
                    ignore_index=True
                )

            self._loaded_lc.add(load_case)
