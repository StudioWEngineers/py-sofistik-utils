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


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderQuadDataTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "QUAD_DATA",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.open()
        self.cdb.quads.data.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = DataFrame(
            {
                "GROUP": [5, 6, 6, 8, 8],
                "ELEM_ID": [51, 63, 65, 83, 85],
                "N1": [1, 1, 1, 1, 1],
                "N2": [2, 2, 2, 2, 2],
                "N3": [3, 3, 3, 3, 3],
                "N4": [4, 4, 3, 4, 3],
                "MNO": [1, 1, 1, 1, 1],
                "NRA": [0, 1, 1, 2, 2],
            }
        ).set_index("ELEM_ID", drop=False)

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(data, self.cdb.quads.data.get_data(), rtol=1E-7)

    def test_get(self) -> None:
        with self.subTest(msg="First node id"):
            self.assertEqual(self.cdb.quads.data.get(51, "N1"), 1)

        with self.subTest(msg="Second node id"):
            self.assertEqual(self.cdb.quads.data.get(63, "N2"), 2)

        with self.subTest(msg="Third node id"):
            self.assertEqual(self.cdb.quads.data.get(65, "N3"), 3)

        with self.subTest(msg="Fourth node id"):
            self.assertEqual(self.cdb.quads.data.get(83, "N4"), 4)

        with self.subTest(msg="MNO"):
            self.assertEqual(self.cdb.quads.data.get(83, "MNO"), 1)

        with self.subTest(msg="NRA"):
            self.assertEqual(self.cdb.quads.data.get(85, "NRA"), 2)

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.quads.data.get(86, "N3")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.quads.data.get(86, "N3", 2), 2)

    def test_get_after_clear(self) -> None:
        self.cdb.quads.data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.quads.data.get(51, "N1")

        self.cdb.quads.data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()
