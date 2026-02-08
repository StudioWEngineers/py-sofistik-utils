# standard library imports
from os import environ
from unittest import TestCase

# third party library imports
from pandas import DataFrame
from pandas.testing import assert_frame_equal

# local library specific imports
from py_sofistik_utils import SOFiSTiKCDBReader


CDB_PATH = environ.get("SOFISTIK_CDB_PATH")
DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
SOFISTIK_VERSION = environ.get("SOFISTIK_VERSION")


_COLUMNS = ["LOAD_CASE","GROUP", "ELEM_ID", "TYPE", "PA", "PE"]

_DATA = [
        (1,  500, 5001, "PG",  +1.0,   -1.0),
        (2,  500, 5001, "PXX", +2.0,   +2.0),
        (6,  500, 5001, "PYP", -6.0,   -6.0),
        (8,  500, 5001, "EX",  -0.008, -0.008),
        (11, 500, 5001, "VX",  +11.0,  +11.0),
        (2,  500, 5009, "PXX", +2.0,   +2.0),
        (6,  500, 5009, "PYP", -6.0,   -6.0),
        (7,  500, 5009, "PZP", -7.0,   -7.0),
        (11, 500, 5009, "VX",  +11.0,  +11.0),
        (3,  501, 5011, "PYY", -3.0,   -3.0),
        (4,  501, 5011, "PZZ", -4.0,   -4.0),
        (5,  501, 5011, "PXP", +5.0,   +5.0),
        (9,  501, 5011, "WX",  +0.009, +0.009),
        (10, 501, 5011, "DT",  -10.0,  -10.0),
        (11, 501, 5011, "VX",  +11.0,  +11.0),
        (3,  501, 5014, "PYY", -3.0,   -3.0),
        (5,  501, 5014, "PXP", +5.0,   +5.0),
        (8,  501, 5014, "EX",  -0.008, -0.008),
        (9,  501, 5014, "WX",  +0.009, +0.009),
        (10, 501, 5014, "DT",  -10.0,  -10.0),
        (11, 501, 5014, "VX",  +11.0,  +11.0)
    ]


class SOFiSTiKCDBReaderCableLoadTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `CableLoad` module.
    """
    def setUp(self) -> None:
        if not CDB_PATH:
            self.fail("SOFISTIK_CDB_PATH environment variable is not set")

        if not DLL_PATH:
            self.fail("SOFISTIK_DLL_PATH environment variable is not set")

        if not SOFISTIK_VERSION:
            self.fail("SOFISTIK_VERSION environment variable is not set")

        self.expected_data = DataFrame(_DATA, columns=_COLUMNS).set_index(
            ["ELEM_ID", "LOAD_CASE", "TYPE"], drop=False
        )
        self.load_cases = list(range(1, 12, 1))

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,
            "CABLE_LOAD",
            DLL_PATH,
            int(SOFISTIK_VERSION)
        )
        self.cdb.initialize()
        self.cdb.cable_load.load(self.load_cases)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise
        # (e.g. -0.008 is represented as -0.00800000037997961). The chosen tolerance
        # rtol=1e-7 is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.cable_load.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        self.assertEqual(self.cdb.cable_load.get(5009, 7, "PZP", "PA"), -7.0)

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.cable_load.clear(7)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.test_get()

        self.cdb.cable_load.load(7)
        with self.subTest(msg="Check indexes management"):
            self.test_get()

    def test_get_after_clear_all(self) -> None:
        """Test for the `get` method after a `clear_all` call.
        """
        self.cdb.cable_load.clear_all()
        self.cdb.cable_load.load(self.load_cases)

        self.test_get()
