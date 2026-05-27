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

_COLUMNS = [
    "GROUP",
    "GROUP_NAME",
    "BEAM_MIN_ID",
    "BEAM_MAX_ID",
    "NUMBER_OF_BEAMS",
    "TRUSS_MIN_ID",
    "TRUSS_MAX_ID",
    "NUMBER_OF_TRUSSES",
    "CABLE_MIN_ID",
    "CABLE_MAX_ID",
    "NUMBER_OF_CABLES",
    "SPRING_MIN_ID",
    "SPRING_MAX_ID",
    "NUMBER_OF_SPRINGS",
    "QUAD_MIN_ID",
    "QUAD_MAX_ID",
    "NUMBER_OF_QUADS"
]
_DATA = [
    (3, "GRP 3", 0, 0, 0, 0, 0, 0, 36, 36, 1, 32, 32, 1, 0, 0, 0),
    (10, "GRP 10", 101, 101, 1, 101, 101, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (20, "GRP 20", 202, 202, 1, 0, 0, 0, 206, 206, 1, 0, 0, 0, 0, 0, 0)
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderGroupDataTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "GROUP_DATA",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.groups.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(
            DataFrame(_DATA, columns=_COLUMNS).set_index(["GROUP"], drop=False),
            self.cdb.groups.get_data(),
            rtol=1E-7
        )

    def test_get_after_clear(self) -> None:
        self.cdb.groups.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.groups.get_id_range("BEAM", 10)

        self.cdb.groups.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get_id_range()

    def test_get_group_name(self) -> None:
        self.assertEqual(self.cdb.groups.get_name(10), "GRP 10")

    def test_get_group_number(self) -> None:
        self.assertEqual(self.cdb.groups.get_number("GRP 10"), 10)

    def test_get_id_range(self) -> None:
        with self.subTest():
            self.assertEqual(
                self.cdb.groups.get_id_range("BEAM", 10),
                range(101, 102)
            )

        with self.subTest():
            self.assertTrue(101 in self.cdb.groups.get_id_range("BEAM", 10))
