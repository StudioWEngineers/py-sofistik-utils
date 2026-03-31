# standard library imports
from ctypes import byref, c_int, sizeof

# third party library imports
from pandas import DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CNODE
from . sofistik_utilities import decode_nodal_boundary_condition


class _NodeData:
    """This class provides methods and a data structure to:

        * access keys ``2/00`` of the CDB file;
        * store the retrieved data in a convenient format;
        * provide access to the data after the CDB is closed.

        The underlying data structure is a :class:`pandas.DataFrame` with the
        following columns:

        * ``ID`` node number
        * ``X0`` X-coordinate
        * ``Y0``: Y-coordinate
        * ``Z0``: Z-coordinate
        * ``KFIX``: lateral stiffness
        * ``IS_:USED``: rotational stiffness

        The ``DataFrame`` uses a MultiIndex with level ``ID`` to enable fast
        lookups via the `get` method. The index column is not dropped from the
        ``DataFrame``.

        .. note::

            Not all available quantities are retrieved and stored. In
            particular:

            * internal node id ("INR)
            * additional bit code ("NCOD")

            are currently not included.

            This is a deliberate design choice and may be changed in the future
            without breaking the existing API.
    """
    def __init__(self, dll: SofDll) -> None:
        self._data = DataFrame(
            columns=[
                "ID",
                "X0",
                "Y0",
                "Z0",
                "KFIX",
                "IS_USED"
            ]
        )
        self._dll = dll
        self._is_loaded = False

    def clear(self) -> None:
        """Clear all the loaded data.
        """
        if self._is_loaded:
            self._data = self._data[0:0]
            self._is_loaded = False

    def data(self, deep: bool = True) -> DataFrame:
        """Return the :class:`pandas.DataFrame` containing the loaded key
        ``20/00``.

        Parameters
        ----------
        deep : bool, default True
            When ``deep=True``, a new object will be created with a copy of the
            calling object's data and indices. Modifications to the data or
            indices of the copy will not be reflected in the original object
            (refer to :meth:`pandas.DataFrame.copy` documentation for details).
        """
        return self._data.copy(deep=deep)

    def drop_unused_nodes(self) -> None:
        """Remove all the unused nodes.
        """
        self._data = self._data.loc[self._data.IS_USED, :]

    def get(
            self,
            node_id: int,
            quantity: str,
            default: bool | float | None = None
    ) -> float | int | bool:
        """Retrieve the requested nodal quantity.

        Parameters
        ----------
        node_id : int
            Node number
        quantity : str
            Quantity to retrieve. Must be one of:

            - ``"X0"``
            - ``"Y0"``
            - ``"Z0"``
            - ``"KFIX"``
            - ``"IS_USED"``

        default : float or None, default None
            Value to return if the requested quantity is not found

        Returns
        -------
        value : float
            The requested quantity if found. Otherwise, returns ``default``
            when it is not None.

        Raises
        ------
        LookupError
            If the requested quantity is not found and ``default`` is None.
        """
        try:
            return self._data.at[node_id, quantity]  # type: ignore
        except (KeyError, ValueError) as e:
            if default is not None:
                return default
            raise LookupError(
                f"Node data entry not found for node id {node_id}, and "
                f"quantity {quantity}!"
            ) from e

    def is_loaded(self) -> bool:
        """Return ``True`` if the nodal data have been loaded from the cdb.
        """
        return self._is_loaded

    def load(self) -> None:
        """Retrieve all nodal data. If the key does not exist or it is empty,
        a warning is raised only if ``echo_level > 0``.
        """
        if self._dll.key_exist(20, 0):
            node = CNODE()
            record_length = c_int(sizeof(node))
            return_value = c_int(0)

            self.clear()

            data: list[dict[str, bool | float | int | str]] = []
            first_call = True
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    20,
                    0,
                    byref(node),
                    byref(record_length),
                    0 if first_call else 1
                )

                record_length = c_int(sizeof(node))
                first_call = False
                if return_value.value >= 2:
                    break

                data.append({
                    "ID": node.m_nr,
                    "X0": node.m_xyz[0],
                    "Y0": node.m_xyz[1],
                    "Z0": node.m_xyz[2],
                    "KFIX": decode_nodal_boundary_condition(node.m_kfix),
                    "IS_USED": (node.m_ncod & 2) > 0
                })

            self._data = DataFrame(data).set_index(["ID"], drop=False)
            self._is_loaded = True

    def number_of_nodes(self) -> int:
        """Return the number of nodes.
        """
        return self._data.ID.size
