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
class SOFiSTiKCDBReaderCableDataTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "CABLE_DATA",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.cable.data.load()

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = DataFrame(
            {
                "GROUP": [50, 50],
                "ELEM_ID": [502, 505],
                "N1": [1, 1],
                "N2": [2, 5],
                "L0": [1.7320507764816284, 1.0],
                "PROPERTY": [3, 3]
            }
        ).set_index("ELEM_ID", drop=False)

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(data, self.cdb.cable.data.data(), rtol=1E-7)

    def test_get(self) -> None:
        with self.subTest(msg="First node id"):
            self.assertEqual(self.cdb.cable.data.get(505, "N1"), 1)

        with self.subTest(msg="Second node id"):
            self.assertEqual(self.cdb.cable.data.get(505, "N2"), 5)

        with self.subTest(msg="Initial length"):
            self.assertEqual(
                self.cdb.cable.data.get(502, "L0"),
                1.7320507764816284
            )

        with self.subTest(msg="Property number"):
            self.assertEqual(self.cdb.cable.data.get(502, "PROPERTY"), 3)

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.cable.data.get(505, "N3")

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(self.cdb.cable.data.get(505, "N3", 2), 2)

    def test_get_after_clear(self) -> None:
        self.cdb.cable.data.clear()
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.cable.data.get(505, "N1")

        self.cdb.cable.data.load()
        with self.subTest(msg="Check indexes management"):
            self.test_get()
