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
    "FORCE",
    "TRANSVERSAL_FORCE",
    "MOMENT",
    "DISPLACEMENT",
    "TRANSVERSAL_DISPLACEMENT",
    "ROTATION",
]

_DATA = [
    (1000, 10, 102, 9.0, 0.0, 1.0000000031710769e-29, 0.09000000357627869, 0.07000000029802322, 0.0),
    (1000, 11, 113, 1.0000000031710769e-29, 1.4142135381698608, 1.0000000031710769e-29, 0.11313708126544952, 0.01414213515818119, 0.0),
]


@skipUnless(all([CDB_PATH, DLL_PATH, VERSION]), "SOFiSTiK environment variables not set!")
class SOFiSTiKCDBReaderSpringResultTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `_SpringResult` module.
    """
    def setUp(self) -> None:
        self.expected_data = DataFrame(
            _DATA, columns=_COLUMNS).set_index(["ELEM_ID", "LOAD_CASE"], drop=False)
        self.load_cases = [1000]

        self.cdb = SOFiSTiKCDBReader(CDB_PATH, "SPRING_RESULT", DLL_PATH, int(VERSION))  # type: ignore
        self.cdb.initialize()
        self.cdb.spring_res.load(self.load_cases)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise. The chosen
        # tolerance rtol is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.spring_res.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        with self.subTest(msg="Axial force"):
            self.assertEqual(self.cdb.spring_res.get(102, 1000, "FORCE"), 9)

        with self.subTest(msg="Transversal force"):
            self.assertEqual(self.cdb.spring_res.get(102, 1000, "TRANSVERSAL_FORCE"), 0)

        with self.subTest(msg="Moment"):
            self.assertEqual(
                self.cdb.spring_res.get(113, 1000, "MOMENT"),
                1.0000000031710769e-29
            )

        with self.subTest(msg="Displacement"):
            self.assertEqual(
                self.cdb.spring_res.get(102, 1000, "DISPLACEMENT"),
                0.09000000357627869
            )

        with self.subTest(msg="Transversal displacement"):
            self.assertEqual(
                self.cdb.spring_res.get(102, 1000, "TRANSVERSAL_DISPLACEMENT"),
                0.07000000029802322
            )

        with self.subTest(msg="Rotation"):
            self.assertEqual(self.cdb.spring_res.get(113, 1000, "ROTATION"), 0)

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.spring_res.get(102, 1000, "NON-EXISTING")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.spring_res.get(102, 1000, "NON-EXISTING", 5), 5)

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.spring_res.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.spring_res.get(113, 1000, "MOMENT")

        self.cdb.spring_res.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.spring_res.get(113, 1000, "MOMENT"),
                1.0000000031710769e-29
            )

    def test_get_after_clear_all(self) -> None:
        """Test for the `get` method after a `clear_all` call.
        """
        self.cdb.spring_res.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.spring_res.get(113, 1000, "MOMENT")

        self.cdb.spring_res.load(self.load_cases)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.spring_res.get(113, 1000, "MOMENT"),
                1.0000000031710769e-29
            )

    def test_load_with_duplicated_load_cases(self) -> None:
        """Test for the `load` method with duplicated entries.
        """
        self.cdb.spring_res.clear_all()
        self.cdb.spring_res.load(self.load_cases + [1000])
        self.assertEqual(
                self.cdb.spring_res.get(113, 1000, "MOMENT"),
                1.0000000031710769e-29
            )
