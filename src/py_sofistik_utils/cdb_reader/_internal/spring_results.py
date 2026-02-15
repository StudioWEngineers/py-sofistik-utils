# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import concat, DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CSPRI_RES


class _SpringResults:
    """This class provides methods and a data structure to:

        * access keys ``170/LC`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the following
        columns:

        * ``LOAD_CASE`` load case number
        * ``GROUP`` element group
        * ``ELEM_ID`` element number
        * ``FORCE`` axial force
        * ``TRANSVERSAL_FORCE``: transversal force
        * ``MOMENT``: axial moment
        * ``DISPLACEMENT``: axial displacement
        * ``TRANSVERSAL_DISPLACEMENT``: transversal displacement
        * ``ROTATION``: axial rotation

        The ``DataFrame`` uses a MultiIndex with levels ``ELEM_ID`` and ``LOAD_CASE``
        (in this specific order) to enable fast lookups via the `get` method. The
        index columns are not dropped from the ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In particular:

            * the three components along the global X, Y and Z axes for:
                - spring force
                - spring displacement
            * nonlinear effects
            * all quantities available if a workload has beed defined

            are currently not included. This is a deliberate design choice and may be
            changed in the future without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns = [
                "LOAD_CASE",
                "GROUP",
                "ELEM_ID",
                "FORCE",
                "TRANSVERSAL_FORCE",
                "MOMENT",
                "DISPLACEMENT",
                "TRANSVERSAL_DISPLACEMENT",
                "ROTATION"
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
        """Return the :class:`pandas.DataFrame` containing the loaded keys ``170/LC``.

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
            quantity: str = "FORCE",
            default: float | None = None
        ) -> float:
        """Retrieve the requested cable result.

        Parameters
        ----------
        element_id : int
            Cable element number
        load_case : int
            Load case number
        quantity : str, default "FORCE"
            Quantity to retrieve. Must be one of:

            - ``FORCE`
            - ``TRANSVERSAL_FORCE``
            - ``MOMENT``
            - ``DISPLACEMENT``
            - ``TRANSVERSAL_DISPLACEMENT``
            - ``ROTATION``

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
                f"Spring result entry not found for element id {element_id}, "
                f"load case {load_case}, and quantity {quantity}!"
            ) from e

    def load(self, load_case: int, grp_divisor: int = 10000) -> None:
        """Load the results for the given ``load_case``.
        """
        if self._dll.key_exist(170, load_case):
            spring = CSPRI_RES()
            record_length = c_int(sizeof(spring))
            return_value = c_int(0)

            if load_case not in self._loaded_lc:
                self._displacements[load_case] = {}
                self._forces[load_case] = {}
                self._moment[load_case] = {}
                self._rotation[load_case] = {}

            else:
                self.clear(load_case)

            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    170,
                    load_case,
                    byref(spring),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                spring_nmb: int = spring.m_nr
                if spring_nmb == 0:
                    record_length = c_int(sizeof(spring))
                    count += 1
                    continue

                grp_nmp = spring.m_nr // grp_divisor

                if grp_nmp not in self._displacements[load_case]:
                    self._displacements[load_case].update({grp_nmp: {}})
                    self._forces[load_case].update({grp_nmp: {}})
                    self._moment[load_case].update({grp_nmp: {}})
                    self._rotation[load_case].update({grp_nmp: {}})

                self._displacements[load_case][grp_nmp].update(
                    {spring_nmb: array([spring.m_v,
                                           spring.m_vt,
                                           spring.m_vtx,
                                           spring.m_vty,
                                           spring.m_vtz], dtype = float64)})

                self._rotation[load_case][grp_nmp].update({spring_nmb: spring.m_phi})

                self._forces[load_case].update(
                    {spring_nmb: array(
                        [spring.m_p,
                         spring.m_pt,
                         spring.m_ptx,
                         spring.m_pty,
                         spring.m_ptz], dtype = float64)})

                self._moment[load_case].update({spring_nmb: spring.m_m})

                record_length = c_int(sizeof(spring))
                count += 1

            self._loaded_lc.add(load_case)
