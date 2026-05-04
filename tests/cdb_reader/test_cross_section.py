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


_COLUMNS = ["ID", "MNO", "A", "AY", "AZ", "IT", "IY", "IZ", "EM", "GM", "SW"]
_DATA = [
    [
        1,
        1,
        0.002827433869242668,
        0.0014635431580245495,
        0.0014635431580245495,
        5.748745934397448e-06,
        2.8981196464883396e-06,
        2.8981196464883396e-06,
        210000000.0,
        80769232.0,
        78.5
    ], [
        2,
        1,
        0.011550000868737698,
        0.009624997153878212,
        0.009624997153878212,
        4.400995294417953e-06,
        1.1790625649155118e-06,
        0.00010481627396075055,
        210000000.0,
        80769232.0,
        78.5
    ], [
        3,
        1,
        0.07920000702142715,
        0.007898920215666294,
        0.05482666194438934,
        0.0024296531919389963,
        0.009423041716217995,
        0.0008479201351292431,
        210000000.0,
        80769232.0,
        78.5
    ]
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderCrossSectionTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "CROSS-SECTION",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.cross_section.load([1, 2, 3])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = DataFrame(_DATA, columns=_COLUMNS).set_index(["ID"], drop=False)

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(data, self.cdb.cross_section.get_data(), rtol=1E-7)

    def test_get(self) -> None:
        with self.subTest(msg="Existing entry - area"):
            self.assertEqual(
                self.cdb.cross_section.get(1, "A"),
                0.002827433869242668
            )

        with self.subTest(msg="Existing entry - AY"):
            self.assertEqual(
                self.cdb.cross_section.get(3, "AY"),
                0.007898920215666294
            )

        with self.subTest(msg="Existing entry - AZ"):
            self.assertEqual(
                self.cdb.cross_section.get(2, "AZ"),
                0.009624997153878212
            )

        with self.subTest(msg="Existing entry - IT"):
            self.assertEqual(
                self.cdb.cross_section.get(3, "IT"),
                0.0024296531919389963
            )

        with self.subTest(msg="Existing entry - IY"):
            self.assertEqual(
                self.cdb.cross_section.get(1, "IY"),
                2.8981196464883396e-06
            )

        with self.subTest(msg="Existing entry - IZ"):
            self.assertEqual(
                self.cdb.cross_section.get(2, "IZ"),
                0.00010481627396075055
            )

        with self.subTest(msg="Existing entry - EM"):
            self.assertEqual(self.cdb.cross_section.get(1, "EM"), 210000000)

        with self.subTest(msg="Existing entry - GM"):
            self.assertEqual(self.cdb.cross_section.get(1, "GM"), 80769232)

        with self.subTest(msg="Existing entry - SW"):
            self.assertEqual(self.cdb.cross_section.get(1, "SW"), 78.5)

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.cross_section.get(4, "EM", -3), -3)

    def test_get_after_clear(self) -> None:
        self.cdb.cross_section.clear(2)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.cross_section.get(2, "A")

        self.cdb.cross_section.load(2)
        with self.subTest(msg="Check indexes management"):
            self.test_get()

    def test_get_after_clear_all(self) -> None:
        self.cdb.cross_section.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.cross_section.get(2, "A")

        self.cdb.cross_section.load([1, 2, 3])
        with self.subTest(msg="Check indexes management"):
            self.test_get()
