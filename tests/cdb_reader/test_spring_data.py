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


@skipUnless(all([CDB_PATH, DLL_PATH, VERSION]), "SOFiSTiK environment variables not set!")
class SOFiSTiKCDBReaderSpringDataTestSuite(TestCase):
    """Tests for the `_SpringData` class.
    """
    def setUp(self) -> None:
        self.expected_data = DataFrame(
            {
                "GROUP": [10, 20],
                "ELEM_ID": [1001, 2020],
                "N1": [1, 2],
                "N2": [2, 0],
                "CP": [1.0, 0.0],
                "CT": [2.5, 0.0],
                "CM": [0.0, 1.5],
            }
        ).set_index("ELEM_ID", drop=False)

        self.cdb = SOFiSTiKCDBReader(CDB_PATH, "SPRING_DATA", DLL_PATH, int(VERSION))  # type: ignore
        self.cdb.initialize()
        self.cdb.spring_data.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise. The chosen
        # tolerance is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.spring_data.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        with self.subTest(msg="First node id"):
            self.assertEqual(self.cdb.spring_data.get(1001, "N1"), 1)

        with self.subTest(msg="Second node id"):
            self.assertEqual(self.cdb.spring_data.get(2020, "N2"), 0)

        with self.subTest(msg="CP"):
            self.assertEqual(self.cdb.spring_data.get(1001, "CP"), 1.0)

        with self.subTest(msg="CT"):
            self.assertEqual(self.cdb.spring_data.get(1001, "CT"), 2.5)

        with self.subTest(msg="CM"):
            self.assertEqual(self.cdb.spring_data.get(2020, "CM"), 1.5)

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.spring_data.get(505, "N3")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.spring_data.get(2021, "CM", 9), 9)

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.spring_data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.spring_data.get(1001, "CM")

        self.cdb.spring_data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()

    def test_has_stiffness(self) -> None:
        """Test for the `has_stiffness` method.
        """
        with self.subTest(msg="Positive check"):
            self.assertTrue(self.cdb.spring_data.has_stiffness(1001, "CP"))

        with self.subTest(msg="Positive check"):
            self.assertFalse(self.cdb.spring_data.has_stiffness(1001, "CM"))
