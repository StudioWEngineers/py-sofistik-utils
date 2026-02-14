# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . group_data import _GroupData
from . sofistik_dll import SofDll
from . sofistik_classes import CCABL_RES


class _CableResults:
    """This class provides methods and a data structure to:

        * access keys ``162/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the following
        columns:

        * ``LOAD_CASE`` load case number
        * ``GROUP`` element group
        * ``ELEM_ID`` element number
        * ``AXIAL_FORCE`` axial force
        * ``AVG_AXIAL_FORCE``: average axial force
        * ``AXIAL_DISPLACEMENT``: axial displacement
        * ``RELAXED_LENGTH``: relaxed cable length
        * ``TOTAL_STRAIN``: total strain
        * ``EFFECTIVE_STIFFNESS``: effective stiffness

        The ``DataFrame`` uses a MultiIndex with levels ``ELEM_ID`` and ``LOAD_CASE``
        (in this specific order) to enable fast lookups via the `get` method. The
        index columns are not dropped from the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In particular:

            * the maximum suspension of cable across axis and its components along the
              global X, Y and Z axes
            * vertical suspension of cable in load direction
            * nonlinear effects

            are currently not included. This is a deliberate design choice and may be
            changed in the future without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data: DataFrame = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "AXIAL_FORCE",
                "AVG_AXIAL_FORCE",
                "AXIAL_DISPLACEMENT",
                "RELAXED_LENGTH",
                "TOTAL_STRAIN",
                "EFFECTIVE_STIFFNESS"
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

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded keys ``162/LC``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the calling
            object's data and indices. Modifications to the data or indices of the
            copy will not be reflected in the original object (refer to
            :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def get(
            self,
            element_id: int,
            load_case: int,
            quantity: str = "AXIAL_FORCE",
            default: float | None = None
        ) -> float:
        """Retrieve the requested cable result.

        Parameters
        ----------
        element_id : int
            Cable element number
        load_case : int
            Load case number
        quantity : str, default "AXIAL_FORCE"
            Quantity to retrieve. Must be one of:

            - ``"AXIAL_FORCE"``
            - ``"AVG_AXIAL_FORCE"``
            - ``"TOTAL_STRAIN"``
            - ``"RELAXED_LENGTH"``
            - ``"AXIAL_DISPLACEMENT"``
            - ``"EFFECTIVE_STIFFNESS"``

        default : float or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float
            The requested value if found. If not found, returns ``default`` when it is not
            None.

        Raises
        ------
        LookupError
            If the requested result is not found and ``default`` is None.
        """
        try:
            return self._data.at[(element_id, load_case), quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Cable result entry not found for element id {element_id}, "
                f"load case {load_case}, and quantity {quantity}!"
            ) from e

    def load(self, load_cases: int | list[int]) -> None:
        """Retrieve cable results for the given ``load_cases``. If a load case is not
        found, a warning is raised only if ``echo_level > 0``.

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
        temp_list: list[dict[str, float | int | str]] = []
        for load_case in load_cases:
            if self._dll.key_exist(162, load_case):
                self.clear(load_case)
                temp_list.extend(self._load(load_case))

        # assigning groups
        group_data = _GroupData(self._dll)
        group_data.load()

        temp_df = DataFrame(temp_list).sort_values("ELEM_ID", kind="mergesort")
        elem_ids = temp_df["ELEM_ID"]

        for grp, grp_range in group_data.iterator_cable():
            if grp_range.stop == 0:
                continue

            left = elem_ids.searchsorted(grp_range.start, side="left")
            right = elem_ids.searchsorted(grp_range.stop - 1, side="right")
            temp_df.loc[temp_df.index[left:right], "GROUP"] = grp

        # set indices for fast lookup
        temp_df = temp_df.set_index(["ELEM_ID", "LOAD_CASE"], drop=False)

        # merge data
        if self._data.empty:
            self._data = temp_df
        else:
            self._data = concat([self._data, temp_df])
        self._loaded_lc.update(load_cases)

    def set_echo_level(self, echo_level: int) -> None:
        """Set the echo level.

        Parameters
        ----------
        echo_level : int
            the new echo level
        """
        self._echo_level = echo_level

    def _load(self, load_case: int) -> list[dict[str, float | int | str]]:
        """Retrieve key ``162/load_case`` using SOFiSTiK dll.
        """
        cable_res = CCABL_RES()
        record_length = c_int(sizeof(cable_res))
        return_value = c_int(0)

        data: list[dict[str, float | int | str]] = []
        first_call = True
        while return_value.value < 2:
            return_value.value = self._dll.get(
                1,
                162,
                load_case,
                byref(cable_res),
                byref(record_length),
                0 if first_call else 1
            )

            record_length = c_int(sizeof(cable_res))
            first_call = False
            if return_value.value >= 2:
                break

            if cable_res.m_nr > 0:
                data.append(
                    {
                        "LOAD_CASE": load_case,
                        "GROUP": 0,
                        "ELEM_ID": cable_res.m_nr,
                        "AXIAL_FORCE": cable_res.m_n,
                        "AVG_AXIAL_FORCE": cable_res.m_n_m,
                        "AXIAL_DISPLACEMENT": cable_res.m_v,
                        "RELAXED_LENGTH": cable_res.m_l0,
                        "TOTAL_STRAIN": cable_res.m_eps0,
                        "EFFECTIVE_STIFFNESS": cable_res.m_effs,
                    }
                )

        return data
