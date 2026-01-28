# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CN_DISPI


class _NodeResiduals:
    """
    This class provides abstractions to load and access information
    about the nodal residuals for non-linear analyses, contained in keys ``26/LC`` of
    the CDB file.

    Data are stored in a :class:`pandas.DataFrame` having the following columns:

    * ``LOAD_CASE``: load combination number
    * ``ID``: node number
    * ``UX``: X component of the nodal residual displacement (translation)
    * ``UY``: Y component of the nodal residual displacement (translation)
    * ``UZ``: Z component of the nodal residual displacement (translation)
    * ``URX``: X component of the nodal residual displacement (rotation)
    * ``URY``: Y component of the nodal residual displacement (rotation)
    * ``URZ``: Z component of the nodal residual displacement (rotation)
    * ``URB``: twist residual rotation
    * ``PX``: X component of the nodal residual reaction (translation)
    * ``PY``: Y component of the nodal residual reaction (translation)
    * ``PZ``: Z component of the nodal residual reaction (translation)
    * ``MX``: X component of the nodal residual reaction (rotation)
    * ``MY``: Y component of the nodal residual reaction (rotation)
    * ``MZ``: Z component of the nodal residual reaction (rotation)
    * ``MB``: warping residual moment
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_NodeResiduals`` class.
        """
        self._data = DataFrame(
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
        """Clear the residuals for the given ``load case``.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.drop(self._data[self._data.LOAD_CASE == load_case].index)
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear the residuals for all the load cases.
        """
        if not self._loaded_lc:
            return

        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_displacements(self, load_case: int, node_number: int) -> DataFrame:
        """Return the translational components of the displacement residuals for the given
        ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``node_nmb``: int
            Node number

        Raises
        ------
        LookupError
            If the given ``load_case`` or ``node_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            raise LookupError(f"Node {node_number} not found in load case {load_case}!")

        return self._data.loc[lc_mask & id_mask, ("UX", "UY", "UZ")].copy(deep=True)

    def get_reaction_forces(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal translational components of the reaction force residuals for
        the given ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``node_nmb``: int
            Node number

        Raises
        ------
        LookupError
            If the given ``load_case`` or ``node_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            raise LookupError(f"Node {node_number} not found in load case {load_case}!")

        return self._data.loc[lc_mask & id_mask, ("PX", "PY", "PZ")].copy(deep=True)

    def get_reaction_moments(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal rotational components of the residuals forces for the given
        ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``node_nmb``: int
            Node number

        Raises
        ------
        LookupError
            If the given ``load_case`` or ``node_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            raise LookupError(f"Node {node_number} not found in load case {load_case}!")

        return self._data.loc[lc_mask & id_mask, ("MX", "MY", "MZ", "MB")].copy(deep=True)

    def get_rotations(self, load_case: int, node_number: int) -> DataFrame:
        """Return the nodal rotational components of the residuals for the given
        ``load_case``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``node_nmb``: int
            Node number

        Raises
        ------
        LookupError
            If the given ``load_case`` or ``node_nmb`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise LookupError(f"Load case {load_case} not found!")

        id_mask = self._data["ID"] == node_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (id_mask & lc_mask).eq(False).all():
            raise LookupError(f"Node {node_number} not found in load case {load_case}!")

        return self._data.loc[lc_mask & id_mask, ("URX", "URY", "URZ", "URB")].copy(deep=True)

    def load(self, load_case: int) -> None:
        """Load the nodal residuals for the given ``load_case``.
        """
        if self._dll.key_exist(26, load_case):
            node = CN_DISPI()
            rec_length = c_int(sizeof(node))
            return_value = c_int(0)

            self.clear(load_case)

            temp_container: list[dict[str, Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    26,
                    load_case,
                    byref(node),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                rec_length = c_int(sizeof(node))
                count += 1

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

            # remove duplicated data as well as max min values
            del temp_container[0:2]
            del temp_container[-1]

            if self._data.empty:
                self._data = DataFrame(temp_container)
            else:
                self._data = concat(
                    [self._data, DataFrame(temp_container)],
                    ignore_index=True
                )
            self._loaded_lc.add(load_case)
