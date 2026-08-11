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

_COLUMNS = ["GROUP_NAME", "LOAD_CASE", "IS_ACTIVE"]
_DATA = [
    ("TEST", 1000, False),
    ("TEST", 1001, True)
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderSecondaryGroupLCTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "SEC_GROUPS_LC",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.sec_groups_lc.load([1000, 1001])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_active_groups(self) -> None:
        self.assertEqual(self.cdb.sec_groups_lc.active_groups(1001), ["TEST"])

    def test_data(self) -> None:
        assert_frame_equal(
            DataFrame(
                _DATA,
                columns=_COLUMNS
            ).set_index(["GROUP_NAME", "LOAD_CASE"], drop=False),
            self.cdb.sec_groups_lc.get_data(),
            rtol=1E-7
        )

    def test_is_active(self) -> None:
        self.assertFalse(self.cdb.sec_groups_lc.is_active("TEST", 1000))

    def test_is_active_after_clear(self) -> None:
        self.cdb.sec_groups_lc.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.sec_groups_lc.is_active("TEST", 1000)

        self.cdb.sec_groups_lc.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.test_is_active()
