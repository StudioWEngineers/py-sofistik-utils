# standard library imports
from os import environ
from unittest import TestCase

# third party library imports
from pandas import DataFrame
from pandas.testing import assert_frame_equal

# local library specific imports
from py_sofistik_utils.cdb_reader import SOFiSTiKCDBReader


CDB_PATH = environ.get("SOFISTIK_CDB_PATH")
DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
SOFISTIK_VERSION = environ.get("SOFISTIK_VERSION")


class SOFiSTiKCDBReaderCableDataTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `CableData` module.
    """
    def setUp(self) -> None:
        if not CDB_PATH:
            self.fail("SOFISTIK_CDB_PATH environment variable is not set")

        if not DLL_PATH:
            self.fail("SOFISTIK_DLL_PATH environment variable is not set")

        if not SOFISTIK_VERSION:
            self.fail("SOFISTIK_VERSION environment variable is not set")

        self.expected_data = DataFrame(
            {
                "GROUP": [50, 50],
                "ELEM_ID": [502, 505],
                "N1": [1, 1],
                "N2": [2, 5],
                "L0": [1.7320507764816284, 1.0],
                "PROPERTY": [3, 3]
            }
        ).set_index("ELEM_ID", drop=False)

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,
            "CABLE_DATA",
            DLL_PATH,
            int(SOFISTIK_VERSION)
        )
        self.cdb.initialize()
        self.cdb.cable_data.load()


    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise. The chosen
        # tolerance is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.cable_data.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        with self.subTest(msg="First node id"):
            self.assertEqual(self.cdb.cable_data.get(505, "N1"), 1)

        with self.subTest(msg="Second node id"):
            self.assertEqual(self.cdb.cable_data.get(505, "N2"), 5)

        with self.subTest(msg="Initial length"):
            self.assertEqual(self.cdb.cable_data.get(502, "L0"), 1.7320507764816284)

        with self.subTest(msg="Property number"):
            self.assertEqual(self.cdb.cable_data.get(502, "PROPERTY"), 3)

        with self.subTest(msg="Non existing entry"):
            with self.assertRaises(LookupError):
                    self.assertEqual(self.cdb.cable_data.get(505, "N3"), 1)

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.cable_data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.assertEqual(self.cdb.cable_data.get(505, "N1"), 1)

        self.cdb.cable_data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()
