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
    "LOAD_CASE",
    "GROUP",
    "ELEM_ID",
    "AXIAL_FORCE",
    "AXIAL_DISPLACEMENT"
]

_DATA = [
    (1000, 2, 23, 150.0, 0.0012631341814994812),
    (1000, 3, 31, 200.0, 0.0016841789474710822)
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderTrussResultTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "TRUSS_RESULT",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.truss_results.load(1000)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = (
            DataFrame(_DATA, columns=_COLUMNS)
            .set_index(["ELEM_ID", "LOAD_CASE"], drop=False)
        )
        assert_frame_equal(data, self.cdb.truss_results.data(), rtol=1E-10)

    def test_get(self) -> None:
        with self.subTest(msg="Axial force"):
            self.assertEqual(
                self.cdb.truss_results.get(23, 1000, "AXIAL_FORCE"),
                150
            )

        with self.subTest(msg="Axial displacement"):
            self.assertEqual(
                self.cdb.truss_results.get(31, 1000, "AXIAL_DISPLACEMENT"),
                0.0016841789474710822
            )

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.truss_results.get(31, 1000, "NON-EXISTING")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.truss_results.get(31, 1000, "NON-EXISTING", 5),
                5
            )

    def test_get_after_clear(self) -> None:
        self.cdb.truss_results.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.truss_results.get(23, 1000, "AXIAL_FORCE")

        self.cdb.truss_results.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.truss_results.get(23, 1000, "AXIAL_FORCE"),
                150
            )

    def test_get_after_clear_all(self) -> None:
        self.cdb.truss_results.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.truss_results.get(23, 1000, "AXIAL_FORCE")

        self.cdb.truss_results.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.truss_results.get(23, 1000, "AXIAL_FORCE"),
                150
            )

    def test_load_with_duplicated_load_cases(self) -> None:
        self.cdb.truss_results.clear_all()
        self.cdb.truss_results.load([1000, 1000])
        self.assertEqual(
            self.cdb.truss_results.get(31, 1000, "AXIAL_FORCE"),
            200
        )
