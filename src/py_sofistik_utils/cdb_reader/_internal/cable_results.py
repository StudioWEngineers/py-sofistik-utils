# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame, Series

# local library specific imports
from . group_lc_data import _GroupLCData
from . sofistik_dll import SofDll
from . sofistik_classes import CCABL_RES


class _CableResults:
    """
    This class provides methods and data structure to:

    * access and load the keys ``162/LC`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_CableResults`` class.
        """
        self._dll = dll

        self._data: DataFrame = DataFrame(columns = ["LOAD_CASE",
                                                     "GROUP",
                                                     "ELEM_ID",
                                                     "AXIAL_FORCE",
                                                     "AVG_AXIAL_FORCE",
                                                     "AXIAL_DISPLACEMENT",
                                                     "RELAXED_LENGTH",
                                                     "TOTAL_STRAIN",
                                                     "EFFECTIVE_STIFFNESS"])
        self._loaded_lc: set[int] = set()

    def clear(self, load_case: int) -> None:
        """Clear the results for the given ``load_case`` number.
        """
        if load_case not in self._loaded_lc:
            return

        self._data = self._data.drop(self._data[self._data.LOAD_CASE == load_case].index)
        self._loaded_lc.remove(load_case)

    def clear_all(self) -> None:
        """Clear all the results for all the load cases.
        """
        if not self._loaded_lc:
            return

        self._data = self._data[0:0]
        self._loaded_lc.clear()

    def get_group_average_axial_force(
            self,
            load_case: int,
            grp_number: int
        ) -> "Series[float]":
        """Return the cable average axial force for the given ``load_case`` and
        ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.AVG_AXIAL_FORCE[lc_mask & grp_mask].copy(deep = True)

    def get_group_axial_displacement(
            self, load_case: int, grp_number: int) -> "Series[float]":
        """Return the cable axial displacement for the given ``load_case`` and ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.AXIAL_DISPLACEMENT[lc_mask & grp_mask].copy(deep = True)

    def get_group_axial_force(self, load_case: int, grp_number: int) -> "Series[float]":
        """Return the cable axial force for the given ``load_case`` and ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.AXIAL_FORCE[lc_mask & grp_mask].copy(deep = True)

    def get_group_effective_stiffness(
            self,
            load_case: int,
            grp_number: int
        ) -> "Series[float]":
        """Return the cable effective stiffness for the given ``load_case`` and
        ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.EFFECTIVE_STIFFNESS[lc_mask & grp_mask].copy(deep = True)

    def get_group_relaxed_length(
            self, load_case: int, grp_number: int) -> "Series[float]":
        """Return the cable relaxed length for the given ``load_case`` and ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.RELAXED_LENGTH[lc_mask & grp_mask].copy(deep = True)

    def get_group_total_strain(self, load_case: int, grp_number: int) -> "Series[float]":
        """Return the cable total strain for the given ``load_case`` and ``grp_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``grp_number``: int
            The group number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``grp_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        lc_mask = self._data["LOAD_CASE"] == load_case
        grp_mask = self._data["GROUP"] == grp_number

        if grp_mask.eq(False).all():
            err_msg = f"Group {grp_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return self._data.TOTAL_STRAIN[lc_mask & grp_mask].copy(deep = True)

    def get_element_average_axial_force(self,
                                        load_case: int,
                                        element_number: int
        ) -> float:
        """Return a shallow copy of the cable average axial force for the given
        ``load_case`` and ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if elem_mask.eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.AVG_AXIAL_FORCE[lc_mask & elem_mask].item())

    def get_element_axial_displacement(
            self, load_case: int, element_number: int) -> float:
        """Return a shallow copy of the cable axial displacement for the given ``load_case``
        and ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if elem_mask.eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.AXIAL_DISPLACEMENT[lc_mask & elem_mask].item())

    def get_element_axial_force(self, load_case: int, element_number: int) -> float:
        """Return a shallow copy of the cable axial force for the given ``load_case`` and
        ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if (elem_mask & lc_mask).eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.AXIAL_FORCE[lc_mask & elem_mask].values[0])

    def get_element_effective_stiffness(self,
                                        load_case: int,
                                        element_number: int
        ) -> float:
        """Return a shallow copy of the cable effective stiffness for the given
        ``load_case`` and ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if elem_mask.eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.EFFECTIVE_STIFFNESS[lc_mask & elem_mask].item())

    def get_element_relaxed_length(self, load_case: int, element_number: int) -> float:
        """Return a shallow copy of the cable relaxed length for the given ``load_case`` and
        ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if elem_mask.eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.RELAXED_LENGTH[lc_mask & elem_mask].item())

    def get_element_total_strain(self, load_case: int, element_number: int) -> float:
        """Return a shallow copy of the cable total strain for the given ``load_case`` and
        ``element_number``.

        Parameters
        ----------
        ``load_case``: int
            Load case number
        ``element_number``: int
            The cable element number

        Raises
        ------
        RuntimeError
            If the given ``load_case`` or ``element_number`` are not found.
        """
        if load_case not in self._loaded_lc:
            raise RuntimeError(f"Load case {load_case} not found!")

        elem_mask = self._data["ELEM_ID"] == element_number
        lc_mask = self._data["LOAD_CASE"] == load_case

        if elem_mask.eq(False).all():
            err_msg = f"Element {element_number} not found in load case {load_case}!"
            raise RuntimeError(err_msg)

        return float(self._data.TOTAL_STRAIN[lc_mask & elem_mask].item())

    def load(self, load_case: int) -> None:
        """Load the cable results for the given ``load_case`` number.

        Parameters
        ----------
        ``load_case``: int

        Raises
        ------
        RuntimeError
            If the given ``load_case`` is not found.
        """
        if self._dll.key_exist(162, load_case):
            cable_res = CCABL_RES()
            record_length = c_int(sizeof(cable_res))
            return_value = c_int(0)

            self.clear(load_case)

            temp_container = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    162,
                    load_case,
                    byref(cable_res),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                if cable_res.m_nr > 0:
                    temp_container.append({"LOAD_CASE": load_case,
                                           "GROUP": 0,
                                           "ELEM_ID": cable_res.m_nr,
                                           "AXIAL_FORCE": cable_res.m_n,
                                           "AVG_AXIAL_FORCE": cable_res.m_n_m,
                                           "AXIAL_DISPLACEMENT": cable_res.m_v,
                                           "RELAXED_LENGTH": cable_res.m_l0,
                                           "TOTAL_STRAIN": cable_res.m_eps0,
                                           "EFFECTIVE_STIFFNESS": cable_res.m_effs,
                                           })

                record_length = c_int(sizeof(cable_res))
                count += 1

            data = DataFrame(temp_container)

            # assigning groups
            group_lc_data = _GroupLCData(self._dll)
            group_lc_data.load(load_case)

            for grp, cable_range in group_lc_data.iterator_cable(load_case):
                data.loc[data.ELEM_ID.isin(cable_range), "GROUP"] = grp

            if self._data.empty:
                self._data = data
            else:
                self._data = concat([self._data, data], ignore_index=True)
            self._loaded_lc.add(load_case)
