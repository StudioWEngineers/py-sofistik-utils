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
class SOFiSTiKCDBReaderTrussDataTestSuite(TestCase):
    """Tests for the `_TrussData` class.
    """
    def setUp(self) -> None:
        self.expected_data = DataFrame(
            {
                "GROUP": [10, 20],
                "ELEM_ID": [1001, 2002],
                "N1": [1, 2],
                "N2": [2, 3],
                "L0": [5.024937629699707, 5.024937629699707],
                "PROPERTY": [2, 1],
                "GAP": [0.0, 0.0],
            }
        ).set_index("ELEM_ID", drop=False)

        self.cdb = SOFiSTiKCDBReader(CDB_PATH, "TRUSS_DATA", DLL_PATH, int(VERSION))  # type: ignore
        self.cdb.initialize()
        self.cdb.truss.data.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise. The chosen
        # tolerance is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.truss.data.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        with self.subTest(msg="First node id"):
            self.assertEqual(self.cdb.truss.data.get(2002, "N1"), 2)

        with self.subTest(msg="Second node id"):
            self.assertEqual(self.cdb.truss.data.get(1001, "N2"), 2)

        with self.subTest(msg="Initial length"):
            self.assertEqual(self.cdb.truss.data.get(1001, "L0"), 5.024937629699707)

        with self.subTest(msg="Property number"):
            self.assertEqual(self.cdb.truss.data.get(1001, "PROPERTY"), 2)

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.truss.data.get(505, "N3")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.truss.data.get(505, "N3", 9), 9)

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.truss.data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.truss.data.get(1001, "PROPERTY")

        self.cdb.truss.data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()
