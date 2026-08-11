# standard library imports
from os import environ
from unittest import skipUnless, TestCase

# third party library imports

# local library specific imports
from py_sofistik_utils import SOFiSTiKCDBReader


CDB_PATH = environ.get("SOFISTIK_CDB_PATH")
DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
VERSION = environ.get("SOFISTIK_VERSION")


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderLoadCaseTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_RESULTS",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.load_cases.load([10, 1000, 1100])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_get_name(self) -> None:
        self.assertEqual(self.cdb.load_cases.get(10, "NAME"), "LOAD PZZ")

    def test_get_source(self) -> None:
        self.assertEqual(
            self.cdb.load_cases.get(1000, "SOURCE"),
            "ASE 2025-8.0.1008"
        )

    def test_get_theory(self) -> None:
        self.assertEqual(self.cdb.load_cases.get(10, "THEORY"), "1ST ORDER")

    def test_get_type(self) -> None:
        self.assertEqual(self.cdb.load_cases.get(1000, "TYPE"), "LINEAR")
