# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_classes import CSECT
from . sofistik_dll import SofDll


class CrossSectionalData:
    """
    This class provides abstractions to load and access information about
    the cross-sectional values, contained in keys ``9/PROP:0`` (total section)
    of the CDB file. Refer to SOFiHELP - CDBase for further information on this
    key.

    Data are stored in a :class:`pandas.DataFrame` having the following
    columns:

    * ``ID``: property number
    * ``MNO``: material ID of the section
    * ``A``: cross-sectional gross area
    * ``AY``: shear area Y
    * ``AZ``: shear area Z
    * ``IT``: torsional moment of inertia
    * ``IY``: moment of inertia YY
    * ``IZ``: moment of inertia ZZ
    * ``EM``: elastic modulus
    * ``GM``: shear modulus
    * ``SW``: nominal weight (of the material, in kN/m3)

    The ``DataFrame`` uses a MultiIndex with level ``ID`` to enable fast
    lookups via the `get` method. The index column is not dropped from
    the ``DataFrame``.

    .. note::

        Not all available quantities are retrieved and stored. In
        particular:

        * ``MRF``: material ID of the reinforcement
        * ``IYZ``: moment of inertia Y-Z
        * ``YS``: coordinate of elastic centroid
        * ``ZS``: coordinate of elastic centroid
        * ``YSC``: coordinate of shear centre
        * ``ZSC``: coordinate of shear centre

        are currently not included.

        This is a deliberate design choice and may be changed in the future
        without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data_total = DataFrame(
            columns=[
                "ID",
                "MNO",
                "A",
                "AY",
                "AZ",
                "IT",
                "IY",
                "IZ",
                "EM",
                "GM",
                "SW"
            ]
        )
        self._dll = dll
        self._loaded_p: set[int] = set()

    def clear(self, section_id: int) -> None:
        """Clear the loaded data for the given ``section_id``.
        """
        if section_id not in self._loaded_p:
            return

        self._data_total = self._data_total[
            self._data_total.index.get_level_values("ID") != section_id
        ]
        self._loaded_p.remove(section_id)

    def clear_all(self) -> None:
        """Clear the loaded data for all the properties.
        """
        if not self._loaded_p:
            return

        self._data_total = self._data_total[0:0]
        self._loaded_p.clear()

    def get(
            self,
            section_id: int,
            quantity: str,
            default: float | int | None = None
    ) -> float | int:
        """Retrieve the requested nodal load.

        Parameters
        ----------
        section_id : int
            The id of the cross-section
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``MNO``
            - ``A``
            - ``AY``
            - ``AZ``
            - ``IT``
            - ``IY``
            - ``IZ``
            - ``EM``
            - ``GM``
            - ``SW``

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
            If the requested data is not found and ``default`` is None.
        """
        try:
            return self._data_total.loc[section_id, quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Data entry not found for property id {section_id} and "
                f"quantity {quantity}!"
            ) from e

    def get_data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing all the loaded
        properties.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data_total.copy(deep=deep)

    def is_loaded(self, section_id: int) -> bool:
        """Return `True` if the ``section_id`` has been loaded.
        """
        return section_id in self._loaded_p

    def load(self, section_id: int | list[int]) -> None:
        """Load cross-sectional values for the given ``section_id``.
        """
        if isinstance(section_id, int):
            section_id = [section_id]
        else:
            section_id = list(set(section_id))

        # load data
        temp_list: list[dict[str, float | int]] = []
        for p in section_id:
            if self._dll.key_exist(9, p):
                self.clear(p)
                temp_list.extend(self._load(p))

        # set indices for fast lookup
        temp_df = (
            DataFrame(temp_list)
            .set_index(["ID"], drop=False).sort_index()
        )

        # merge data
        if self._data_total.empty:
            self._data_total = temp_df
        else:
            self._data_total = concat([self._data_total, temp_df]).sort_index()
        self._loaded_p.update(section_id)

    def _load(self, section_id: int) -> list[dict[str, float | int]]:
        """Retrieve key ``9/section_id:0`` using SOFiSTiK dll.
        """
        prop = CSECT()
        rec_length = c_int(sizeof(prop))
        return_value = c_int(0)

        data: list[dict[str, float | int]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                9,
                section_id,
                byref(prop),
                byref(rec_length),
                0 if first_call else 1
            )

            rec_length = c_int(sizeof(prop))
            first_call = False
            if return_value.value >= 2:
                break

            if prop.m_id != 0:
                continue

            data.append(
                {
                    "ID": section_id,
                    "MNO": prop.m_mno,
                    "A": prop.m_a,
                    "AY": prop.m_ay,
                    "AZ": prop.m_az,
                    "IT": prop.m_it,
                    "IY": prop.m_iy,
                    "IZ": prop.m_iz,
                    "EM": prop.m_em,
                    "GM": prop.m_gm,
                    "SW": prop.m_gam
                }
            )

        return data
