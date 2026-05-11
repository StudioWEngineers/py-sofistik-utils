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
class SOFiSTiKCDBReaderNodeLoadTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_LOADS",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.node.loads.load([10, 20])

        self.data = DataFrame(
            [
                [10, 1, 0.0,  0.0, -3.0, 0.0,  0.0, 0.0, 0.0],
                [10, 3, 1.0,  0.0,  0.0, 0.0,  0.0, 0.0, 0.0],
                [20, 2, 0.0, -1.0,  0.0, 0.0,  0.0, 0.0, 0.0],
                [20, 2, 0.0, -2.5,  0.0, 0.0,  0.0, 0.0, 0.0],
                [20, 3, 0.0,  0.0,  0.0, 0.0, -1.0, 0.0, 0.0],
            ],
            columns=["LOAD_CASE", "ID", "PX", "PY", "PZ", "MX", "MY", "MZ", "MB"]
        ).set_index(["ID", "LOAD_CASE"], drop=False).sort_index()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(self.cdb.node.loads.get_data(), self.data)

    def test_get(self) -> None:
        with self.subTest(msg="single entry"):
            self.assertEqual(self.cdb.node.loads.get(3, 10, "PX"), 1)

        with self.subTest(msg="multiple entry"):
            self.assertEqual(self.cdb.node.loads.get(2, 20, "PY"), -3.5)

    def test_get_after_clear(self) -> None:
        self.cdb.node.loads.clear(10)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.node.loads.get(3, 10, "PX")

        self.cdb.node.loads.load(10)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(self.cdb.node.loads.get(2, 20, "PY"), -3.5)

    def test_get_after_clear_all(self) -> None:
        self.cdb.node.loads.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.node.loads.get(3, 10, "PX")

        self.cdb.node.loads.load([10, 20])
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(self.cdb.node.loads.get(3, 10, "PX"), 1)

    def test_load_with_duplicated_load_cases(self) -> None:
        self.cdb.node.loads.clear_all()
        self.cdb.node.loads.load([10, 20] + [10])
        self.assertEqual(self.cdb.node.loads.get(2, 20, "PY"), -3.5)
