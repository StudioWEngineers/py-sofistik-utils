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


_COLUMNS = [
    "LOAD_CASE",
    "GROUP",
    "ELEM_ID",
    "AXIAL_FORCE",
    "AVG_AXIAL_FORCE",
    "AXIAL_DISPLACEMENT",
    "RELAXED_LENGTH",
    "TOTAL_STRAIN",
    "EFFECTIVE_STIFFNESS",
]

_DATA = [
    (1000, 10, 101, 1.72499418258667,     1.7248634099960327, 4.0439590520691127e-05, 1.0, 1.0000000031710769e-30, 0.8181666135787964),
    (1001, 10, 101, 31.723800659179688,   31.72079849243164,  8.366186521016061e-04,  1.0, 1.0000000031710769e-30, 0.9982974529266357),
    (1000, 10, 102, 1.7247849702835083,   1.7247587442398071, 4.0434926631860435e-05, 1.0, 1.0000000031710769e-30, 0.8180915713310242),
    (1001, 10, 102, 30.09699058532715,    30.09699058532715,  7.937877089716494e-04,  1.0, 1.0000000031710769e-30, 0.9983730912208557),
    (1000, 10, 103, 1.72499418258667,     1.7248634099960327, 4.0439590520691127e-05, 1.0, 1.0000000031710769e-30, 0.8181666135787964),
    (1001, 10, 103, 31.723800659179688,   31.72079849243164,  8.366186521016061e-04,  1.0, 1.0000000031710769e-30, 0.9982974529266357)
]


class SOFiSTiKCDBReaderCableResultTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `CableResult` module.
    """
    def setUp(self) -> None:
        if not CDB_PATH:
            self.fail("SOFISTIK_CDB_PATH environment variable is not set")

        if not DLL_PATH:
            self.fail("SOFISTIK_DLL_PATH environment variable is not set")

        if not SOFISTIK_VERSION:
            self.fail("SOFISTIK_VERSION environment variable is not set")

        self.expected_data = DataFrame(
            _DATA, columns=_COLUMNS).set_index(["ELEM_ID", "LOAD_CASE"], drop=False)
        self.load_cases = list(range(1000, 1002, 1))

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,
            "CABLE_RESULT",
            DLL_PATH,
            int(SOFISTIK_VERSION)
        )
        self.cdb.initialize()
        self.cdb.cable_res.load(self.load_cases)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        """Test for the `data` method.
        """
        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise. The chosen
        # tolerance rtol is stricter than pandas default and reflects the maximum relative
        # error observed in practice, ensuring stable and reproducible comparisons.
        assert_frame_equal(self.expected_data, self.cdb.cable_res.data(), rtol=1E-7)

    def test_get(self) -> None:
        """Test for the `get` method.
        """
        with self.subTest(msg="Axial force"):
            self.assertEqual(
                self.cdb.cable_res.get(102, 1000, "AXIAL_FORCE"), 1.7247849702835083
            )

        with self.subTest(msg="Average axial force"):
            self.assertEqual(
                self.cdb.cable_res.get(102, 1000, "AVG_AXIAL_FORCE"), 1.7247587442398071
            )

        with self.subTest(msg="Axial displacement"):
            self.assertEqual(
                self.cdb.cable_res.get(101, 1001, "AXIAL_DISPLACEMENT"), 8.366186521016061e-04
            )

        with self.subTest(msg="Relaxed length"):
            self.assertEqual(self.cdb.cable_res.get(103, 1001, "RELAXED_LENGTH"), 1)

        with self.subTest(msg="Total strain"):
            self.assertEqual(
                self.cdb.cable_res.get(102, 1001, "TOTAL_STRAIN"), 1.0000000031710769e-30
            )

        with self.subTest(msg="Effective stiffness"):
            self.assertEqual(
                self.cdb.cable_res.get(102, 1000, "EFFECTIVE_STIFFNESS"), 0.8180915713310242
            )

    def test_get_after_clear(self) -> None:
        """Test for the `get` method after a `clear` call.
        """
        self.cdb.cable_res.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.cable_res.get(102, 1000, "AXIAL_FORCE")

        self.cdb.cable_res.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(self.cdb.cable_res.get(103, 1000, "RELAXED_LENGTH"), 1)

    def test_get_after_clear_all(self) -> None:
        """Test for the `get` method after a `clear_all` call.
        """
        self.cdb.cable_res.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.cable_res.get(102, 1000, "AXIAL_FORCE")

        self.cdb.cable_res.load(self.load_cases)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.cable_res.get(102, 1000, "AXIAL_FORCE"), 1.7247849702835083
            )
