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

_COLUMNS = ["GROUP", "LOAD_CASE", "IS_ACTIVE"]
_DATA = [
    (3, 1000, True),
    (3, 1001, False),
    (10, 1000, False),
    (10, 1001, True),
    (20, 1000, True),
    (20, 1001, True)
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderGroupLCTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "GROUP_LC_DATA",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.groups_lc.load([1000, 1001])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(
            DataFrame(
                _DATA,
                columns=_COLUMNS
            ).set_index(["GROUP", "LOAD_CASE"], drop=False),
            self.cdb.groups_lc.get_data(),
            rtol=1E-7
        )

    def test_is_active(self) -> None:
        self.assertFalse(self.cdb.groups_lc.is_active(10, 1000))

    def test_is_active_after_clear(self) -> None:
        self.cdb.groups_lc.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.groups_lc.is_active(10, 1000)

        self.cdb.groups_lc.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.test_is_active()
