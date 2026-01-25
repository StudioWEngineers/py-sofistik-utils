# standard library imports
from ctypes import byref, c_int, sizeof
from typing import Any

# third party library imports
from pandas import DataFrame

# local library specific imports
from . sofistik_dll import SofDll
from . sofistik_classes import CNODE
from . sofistik_utilities import decode_nodal_boundary_condition


class _NodeData:
    """
    The ``_NodeData`` class provides methods and data structure to:

    * access and load the keys ``20/00`` of the CDB file;
    * store these data in a convenient format;
    * provide access to these data.

    Node data are stored in a :class:`pandas.DataFrame` with the following columns:

    * ``ID``: the node number
    * ``INT_ID``: the node internal number
    * ``X0``: the X coordinate of the node
    * ``Y0``: the Y coordinate of the node
    * ``Z0``: the Z coordinate of the node
    * ``KFIX``: string defining the boundary conditions defined for the node
    * ``IS_USED``: `bool`, `True` if the node is connected to already engaged nodes
    """
    def __init__(self, dll: SofDll) -> None:
        """The initializer of the ``_NodeData`` class.
        """
        self._data = DataFrame(
            columns = ["ID", "INT_ID", "X0", "Y0", "Z0", "KFIX", "IS_USED"]
        )
        self._dll = dll
        self._is_loaded = False

    def clear(self) -> None:
        """Clear the nodal information.
        """
        if self._is_loaded:
            self._data = self._data[0:0]
            self._is_loaded = False

    def drop_not_used_nodes(self) -> None:
        """Remove all the not used nodes.
        """
        self._data = self._data.loc[self._data.IS_USED, :]

    def get_all_coordinates(self) -> Any:
        """Return all the nodal coordinates.
        """
        return self._data[["ID", "X0", "Y0", "Z0"]].copy(deep=True)

    def get_boundary_condition(self, node_number: int) -> str:
        """Return the nodal boundary conditions for the given ``node_number``.

        Parameters
        ----------
        ``node_number``: int

        Raises
        ------
        RuntimeError
            If the given ``node_number`` is not found.
        """
        mask = self._data["ID"] == node_number

        if mask.eq(False).all():
            raise RuntimeError(f"Node number {node_number} not found!")

        return self._data.KFIX[mask].item()  #type: ignore

    def get_coordinates(self, node_number: int) -> Any:
        """Return the nodal coordinates for the given ``node_number``.

        Parameters
        ----------
        ``node_number``: int

        Raises
        ------
        RuntimeError
            If the given ``node_number`` is not found.
        """
        mask = self._data["ID"] == node_number

        if mask.eq(False).all():
            raise RuntimeError(f"Node number {node_number} not found!")

        return self._data[["X0", "Y0", "Z0"]][mask].copy(deep=True)

    def get_number_of_nodes(self) -> int:
        """Return the number of nodes.
        """
        return self._data.ID.size

    def is_loaded(self) -> bool:
        """Return ``True`` if the nodal data have been loaded from the cdb.
        """
        return self._is_loaded

    def load(self) -> None:
        """Load nodal data for all the nodes.
        """
        if self._dll.key_exist(20, 0):
            node = CNODE()
            record_length = c_int(sizeof(node))
            return_value = c_int(0)

            self.clear()

            temp_container: list[dict[str, Any]] = []
            count = 0
            while return_value.value < 2:
                return_value.value = self._dll.get(
                    1,
                    20,
                    0,
                    byref(node),
                    byref(record_length),
                    0 if count == 0 else 1
                )

                if return_value.value >= 2:
                    break

                temp_container.append({
                    "ID": node.m_nr,
                    "INT_ID": node.m_inr,
                    "X0": node.m_xyz[0],
                    "Y0": node.m_xyz[1],
                    "Z0": node.m_xyz[2],
                    "KFIX": decode_nodal_boundary_condition(node.m_kfix),
                    "NOT_USED": (node.m_ncod & 3) > 0
                })

                record_length = c_int(sizeof(node))
                count += 1

            self._data = DataFrame(temp_container)
            self._is_loaded = True
