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
    "GROUP",
    "ELEM_ID",
    "N1",
    "N2",
    "LENGTH",
    "T00",
    "T01",
    "T02",
    "T10",
    "T11",
    "T12",
    "T20",
    "T21",
    "T22",
    "PROP_END_1",
    "PROP_END_2",
    "RELEASES_END_1",
    "RELEASES_END_2"
]
_DATA = [
    [
        10,
        101,
        1,
        2,
        5.024937629699707,
        0.9950371980667114,
        0.0,
        -0.09950372576713562,
        0.0,
        -1.0,
        0.0,
        -0.09950372576713562,
        -0.0,
        -0.9950371980667114,
        1,
        1,
        "MT",
        ""
    ],
    [
        20,
        202,
        2,
        3,
        5.024937629699707,
        0.9950371980667114,
        0.0,
        -0.09950372576713562,
        0.0,
        -1.0,
        0.0,
        -0.09950372576713562,
        -0.0,
        -0.9950371980667114,
        1,
        2,
        "",
        "NMYMZ"
    ]
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderBeamDataTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "BEAM_DATA",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.beams.data.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = DataFrame(
            _DATA,
            columns=_COLUMNS
        ).set_index(["ELEM_ID"], drop=False)

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(data, self.cdb.beams.data.get_data(), rtol=1E-7)

    def test_get(self) -> None:
        with self.subTest(msg="Existing entry - length"):
            self.assertEqual(self.cdb.beams.data.get(202), 5.024937629699707)

        with self.subTest(msg="Existing entry - N1"):
            self.assertEqual(self.cdb.beams.data.get(202, "N1"), 2)

        with self.subTest(msg="Existing entry - N2"):
            self.assertEqual(self.cdb.beams.data.get(101, "N2"), 2)

        with self.subTest(msg="Existing entry - T00"):
            self.assertEqual(
                self.cdb.beams.data.get(202, "T00"),
                0.9950371980667114
            )

        with self.subTest(msg="Existing entry - T21"):
            self.assertEqual(self.cdb.beams.data.get(101, "T21"), 0)

        with self.subTest(msg="Existing entry - PROP_END_1"):
            self.assertEqual(self.cdb.beams.data.get(202, "PROP_END_1"), 1)

        with self.subTest(msg="Existing entry - PROP_END_2"):
            self.assertEqual(self.cdb.beams.data.get(202, "PROP_END_2"), 2)

        with self.subTest(msg="Existing entry - RELEASES_END_1"):
            self.assertEqual(
                self.cdb.beams.data.get(202, "RELEASES_END_1"),
                ""
            )

        with self.subTest(msg="Existing entry - RELEASES_END_2"):
            self.assertEqual(
                self.cdb.beams.data.get(202, "RELEASES_END_2"),
                "NMYMZ"
            )

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.beams.data.get(101, "PA", -3),
                -3
            )

    def test_get_after_clear(self) -> None:
        self.cdb.beams.data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.beams.data.get(202)

        self.cdb.beams.data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()

    def test_is_loaded(self) -> None:
        with self.subTest(msg="After load"):
            self. assertTrue(self.cdb.beams.data.is_loaded())

        self.cdb.beams.data.clear()
        with self.subTest(msg="After clear"):
            self. assertFalse(self.cdb.beams.data.is_loaded())
