# standard library imports
from os import environ
from unittest import skipUnless, TestCase

# third party library imports
from pandas import DataFrame
from pandas.testing import assert_frame_equal

# local library specific imports
from py_sofistik_utils import SOFiSTiKCDBReader


CDB_PATH = environ.get("SOFISTIK_CDB_PATH")
DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
VERSION = environ.get("SOFISTIK_VERSION")


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderNodeDataTestSuite(TestCase):
    """Tests contiguous node numbering.
    """
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_DATA",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.node.data.load()

        self.data = DataFrame(
            [
                [1, 0.0, 0.0, 0.0, "PP", False],
                [2, 0.0, 1.0, 0.0, "PPMX", False],
                [3, 0.0, 2.0, 0.0, "XPMX", False],
                [4, 1.0, 0.0, 0.0, "PP", False],
                [5, 1.0, 1.0, 0.0, "PP", False],
                [6, 1.0, 2.0, 0.0, "FREE", False],
                [7, 2.0, 0.0, 0.0, "FREE", False],
                [8, 2.0, 1.0, 0.0, "PP", False],
                [9, 2.0, 2.0, 0.0, "F", False],
                [10, 3.0, 0.0, 0.0, "FREE", False],
                [11, 3.0, 1.0, 0.0, "FREE", False],
                [12, 3.0, 2.0, 0.0, "FREE", False]
            ],
            columns=["ID", "X0", "Y0", "Z0", "KFIX", "IS_USED"]
        ).set_index("ID", drop=False)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(self.cdb.node.data.data(), self.data)

    def test_drop_unused_nodes(self) -> None:
        self.cdb.node.data.drop_unused_nodes()
        assert_frame_equal(
            self.cdb.node.data.data(),
            self.data.loc[self.data.IS_USED, :]
        )

    def test_get_boundary_condition(self) -> None:
        for node_id in range(1, 13, 1):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "KFIX"),
                    self.data.KFIX[node_id]
                )

        # second run to check pointer rewinding
        self.cdb.node.data.clear()
        self.cdb.node.data.load()
        for node_id in range(1, 13, 1):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "KFIX"),
                    self.data.KFIX[node_id]
                )

    def test_get_coordinates(self) -> None:
        for node_id in range(1, 13, 1):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "X0"),
                    self.data.X0[node_id]
                )

        # second run to check pointer rewinding
        self.cdb.node.data.clear()
        self.cdb.node.data.load()
        for node_id in range(1, 13, 1):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "Y0"),
                    self.data.Y0[node_id]
                )

    def test_number_of_nodes(self) -> None:
        self.assertEqual(self.cdb.node.data.number_of_nodes(), 12)


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderEnhancedNodeDataTestSuite(TestCase):
    """Tests non-contiguous node numbering as well as not used nodes.
    """
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_DATA_NON_CONTIGUOUS_AND_FREE",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.node.data.load()

        self.data = DataFrame(
            [
                [1, 0.0, 0.0, 0.0, "FREE", True],
                [3, 1.0, 0.0, 0.0, "FREE", True],
                [5, 1.0, 1.0, 0.0, "FREE", True],
                [7, 0.0, 1.0, 0.0, "FREE", True],
                [9, 0.5, 0.5, 0.0, "FREE", False]
            ],
            columns=["ID", "X0", "Y0", "Z0", "KFIX", "IS_USED"]
        ).set_index("ID", drop=False)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(self.cdb.node.data.data(), self.data)

    def test_drop_not_used_nodes(self) -> None:
        self.cdb.node.data.drop_unused_nodes()
        assert_frame_equal(
            self.cdb.node.data.data(),
            self.data.loc[self.data.IS_USED, :]
        )

    def test_get_boundary_condition(self) -> None:
        for node_id in range(1, 10, 2):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "KFIX"),
                    self.data.KFIX[node_id]
                )

        # second run to check pointer rewinding
        self.cdb.node.data.clear()
        self.cdb.node.data.load()
        for node_id in range(1, 10, 2):
            with self.subTest(row_index=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "KFIX"),
                    self.data.KFIX[node_id]
                )

    def test_get_coordinates(self) -> None:
        for node_id in range(1, 10, 2):
            with self.subTest(node_id=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "X0"),
                    self.data.X0[node_id]
                )

        # second run to check pointer rewinding
        self.cdb.node.data.clear()
        self.cdb.node.data.load()
        for node_id in range(1, 10, 2):
            with self.subTest(node_id=node_id):
                self.assertEqual(
                    self.cdb.node.data.get(node_id, "Y0"),
                    self.data.Y0[node_id]
                )

    def test_number_of_nodes(self) -> None:
        self.assertEqual(self.cdb.node.data.number_of_nodes(), 5)
