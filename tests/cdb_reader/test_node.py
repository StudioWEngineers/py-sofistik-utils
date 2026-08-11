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

_COLUMNS = ["LOAD_CASE", "ID", "X", "Y", "Z"]
_DATA = [
    (
        1000,
        1,
        0.0 + 0.0,
        0.0 + 0.0,
        0.0 + 0.0
    ), (
        1000,
        9,
        5.0 + 0.0,
        0.0 + 0.0,
        0.0 + 0.0
    ), (
        1000,
        12,
        -7.007679960224777e-05 + 1.5,
        -0.0888170599937439 + 0.0,
        -0.01165119931101799 + 0.0
    ), (
        1100,
        1,
        0.0 + 0.0,
        0.0 + 0.0,
        0.0 + 0.0
    ), (
        1100,
        9,
        5.0 + 0.0,
        0.0 + 0.0,
        0.0 + 0.0
    ), (
        1100,
        12,
        -7.007679960224777e-05 + 1.5,
        -0.0888170599937439 + 0.0,
        -0.01165119931101799 + 0.0
    )
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderNodeTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_RESULTS",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.nodes.data.load()
        self.cdb.nodes.results.load([1000, 1100])
        self.cdb.nodes.calculate_deflected_configuration(1000)
        self.cdb.nodes.calculate_deflected_configuration(1100)

        self.data = (
            DataFrame(_DATA, columns=_COLUMNS)
            .set_index(["LOAD_CASE", "ID"], drop=False)
        ).reset_index(drop=True)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_get_deflected_configuration(self) -> None:
        assert_frame_equal(
            self.cdb.nodes.get_deflected_configuration(1000),
            self.data.loc[self.data["LOAD_CASE"] == 1000]
        )

    def test_get_deflected_configuration_after_clear(self) -> None:
        self.cdb.nodes.clear(1000)
        with self.subTest(msg="Before recalculating"):
            with self.assertRaises(LookupError):
                self.cdb.nodes.get_deflected_configuration(1000)

        self.cdb.nodes.calculate_deflected_configuration(1000)
        with self.subTest(msg="After recalculating"):
            assert_frame_equal(
                self.cdb.nodes.get_deflected_configuration(
                    1000
                ).reset_index(drop=True),
                self.data.loc[self.data["LOAD_CASE"] == 1000]
            )

    def test_get_deflected_configuration_after_clear_all(self) -> None:
        self.cdb.nodes.clear_all()
        with self.subTest(msg="Before recalculating"):
            with self.assertRaises(LookupError):
                self.cdb.nodes.get_deflected_configuration(1000)

        self.cdb.nodes.calculate_deflected_configuration(1000)
        with self.subTest(msg="After recalculating"):
            assert_frame_equal(
                self.cdb.nodes.get_deflected_configuration(
                    1000
                ).reset_index(drop=True),
                self.data.loc[self.data["LOAD_CASE"] == 1000]
            )
