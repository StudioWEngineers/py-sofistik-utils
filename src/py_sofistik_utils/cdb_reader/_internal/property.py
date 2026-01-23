"""
PropertyData
------------

The `PropertyData` class provides abstractions to load and access information about the
cross-sectional values, contained in keys `9/PROP:0` (total section) of the CDB file.
Refer to SOFiHELP - CDBase for further information on this key.

Data are stored in a `pandas` `DataFrame` having the following columns:
    * `ID`: property number
    * `A`: cross-sectional gross area
    * `AV_Y`: shear area Y
    * `AV_Z`: shear area Z
    * `J`: torsional moment of inertia
    * `I_YY`: moment of inertia YY
    * `I_ZZ`: moment of inertia ZZ
    * `E`: elastic modulus
    * `G`: shear modulus
    * `SW`: nominal weight (of the material)
"""
# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CSECT, CSECT_ADD


class PropertyData:
    """The `PropertyData` class provides abstractions to load and access information about
    the cross-sectional values, contained in keys `9/PROP:0` (total section) of the CDB
    file. Refer to SOFiHELP - CDBase for further information on this key.

    Data are stored in a `pandas` `DataFrame` having the following columns:
        * `ID`: property number
        * `A`: cross-sectional gross area
        * `AV_Y`: shear area Y
        * `AV_Z`: shear area Z
        * `J`: torsional moment of inertia
        * `I_YY`: moment of inertia YY
        * `I_ZZ`: moment of inertia ZZ
        * `W_EL_YY`: elastic section modulus YY
        * `W_EL_ZZ`: elastic section modulus ZZ
        * `E`: elastic modulus
        * `G`: shear modulus
        * `SW`: nominal weight (of the material)
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the `PropertyData` class.
        """
        self._data = DataFrame(
            columns = [
                "ID",
                "A",
                "AV_Y",
                "AV_Z",
                "J",
                "I_YY",
                "I_ZZ",
                "W_EL_YY",
                "W_EL_ZZ",
                "E", "G",
                "SW"
            ]
        )
        self._dll = dll
        self._loaded_prop: set[int] = set()

    def clear(self, property_number: int) -> None:
        """Clear values for the given `property_number`.
        """
        if property_number not in self._loaded_prop:
            return

        self._data = self._data.drop(self._data[self._data.ID == property_number].index)
        self._loaded_prop.remove(property_number)

    def clear_all(self) -> None:
        """Clear values for all the properties.
        """
        self._data = self._data[0:0]
        self._loaded_prop.clear()

    def get_area(self, property_number: int) -> float:
        """Return the cross-sectional gross area for the given `property_number`.

        Parameters
        ----------
        `property_number`: int
            The property number

        Raises
        ------
        LookupError
            If the given `property_number` is not found.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask, ("A")].item()  #type: ignore

    def get_elastic_section_modulus_yy(self, property_number: int) -> float:
        """Return the elastic section modulus YY for the given `property_number`.

        Parameters
        ----------
        `property_number`: int
            The property number

        Raises
        ------
        LookupError
            If the given `property_number` is not found.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask, ("W_EL_YY")].item()  #type: ignore

    def get_elastic_section_modulus_zz(self, property_number: int) -> float:
        """Return the elastic section modulus ZZ for the given `property_number`.

        Parameters
        ----------
        `property_number`: int
            The property number

        Raises
        ------
        LookupError
            If the given `property_number` is not found.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask, ("W_EL_ZZ")].item()  #type: ignore

    def get_second_moment_of_area_yy(self, property_number: int) -> float:
        """Return the cross-sectional moment of area YY for the given `property_number`.

        Parameters
        ----------
        `property_number`: int
            The property number

        Raises
        ------
        LookupError
            If the given `property_number` is not found.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask, ("I_YY")].item()  #type: ignore

    def get_second_moment_of_area_zz(self, property_number: int) -> float:
        """Return the cross-sectional moment of area ZZ for the given `property_number`.

        Parameters
        ----------
        `property_number`: int
            The property number

        Raises
        ------
        LookupError
            If the given `property_number` is not found.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask, ("I_ZZ")].item()  #type: ignore

    def get_values(self, property_number: int) -> DataFrame:
        """Return all the sectional values for the given `property_number`.
        """
        if property_number not in self._loaded_prop:
            raise LookupError(f"Property number {property_number} not found!")

        p_mask = self._data["ID"] == property_number
        return self._data.loc[p_mask].copy(deep=True)

    def load(self, property_number: int) -> None:
        """Load sectional values for the given `property_number`.
        """
        if self._dll.key_exist(9, property_number):
            prop = CSECT()
            rec_length = c_int(sizeof(prop))
            return_value = c_int(0)

            prop_add = CSECT_ADD()
            rec_length_add = c_int(sizeof(prop_add))
            return_value_add = c_int(0)

            self.clear(property_number)

            temp_container: list[Any] = [0 for _ in range(12)]
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    9,
                    property_number,
                    byref(prop),
                    byref(rec_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                if prop.m_id == 0:
                    temp_container[0] = property_number
                    temp_container[1] = prop.m_a
                    temp_container[2] = prop.m_ay
                    temp_container[3] = prop.m_az
                    temp_container[4] = prop.m_it
                    temp_container[5] = prop.m_iy
                    temp_container[6] = prop.m_iz
                    temp_container[9] = prop.m_em
                    temp_container[10] = prop.m_gm
                    temp_container[11] = prop.m_gam

                else:
                    return_value_add.value = self._dll.get(
                        1,
                        9,
                        property_number,
                        byref(prop_add),
                        byref(rec_length_add),
                        -1
                    )

                    y_max = max(abs(prop_add.m_ymin), prop_add.m_ymax)
                    z_max = max(abs(prop_add.m_zmin), prop_add.m_zmax)

                #TODO: temporary workaround
                if count >= 1:
                    break
                count += 1
                rec_length = c_int(sizeof(prop))

            data = DataFrame(
                [
                    {
                        "ID": property_number,
                        "A": temp_container[1],
                        "AV_Y": temp_container[2],
                        "AV_Z": temp_container[3],
                        "J": temp_container[4],
                        "I_YY": temp_container[5],
                        "I_ZZ": temp_container[6],
                        "W_EL_YY": temp_container[5] / y_max,
                        "W_EL_ZZ": temp_container[6] / z_max,
                        "E": temp_container[9],
                        "G": temp_container[10],
                        "SW": temp_container[11]
                    }
                ]
            )

            if self._data.empty:
                self._data = data
            else:
                self._data = concat([self._data, data], ignore_index=True)

            self._loaded_prop.add(property_number)
