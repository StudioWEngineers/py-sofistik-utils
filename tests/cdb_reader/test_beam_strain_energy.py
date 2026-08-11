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

_COLUMNS = ["ELEM_ID", "GROUP", "LOAD_CASE", "U"]
_DATA = [
    [101, 10, 1000, 0.34917488541448244],
    [102, 10, 1000, 1.2396276374589636],
    [101, 10, 1001, 0.029400526651160386],
    [102, 10, 1001, 0.0],
    [101, 10, 1002, 0.3785754120656428],
    [102, 10, 1002, 1.2396276374589636]
]
_DATA_DIV = [
    [101, 10, 1000, 0.3846355348887977],
    [102, 10, 1000, 0.8608525260131692],
    [101, 10, 1001, 0.029400526651160386],
    [102, 10, 1001, 0.0],
    [101, 10, 1002, 0.41403606153995803],
    [102, 10, 1002, 0.8608525260131692]
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderBeamStrainEnergyTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "BEAM_STRAIN_ENERGY",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.open()
        self.cdb.beams.calculate_strain_energy([1000, 1001, 1002])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_get_strain_energy(self) -> None:
        data = DataFrame(
            _DATA,
            columns=_COLUMNS
        ).set_index(["LOAD_CASE", "ELEM_ID"], drop=False).sort_index()

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(
            data,
            self.cdb.beams.get_strain_energy(),
            rtol=1E-7
        )

    def test_get_element_strain_energy(self) -> None:
        with self.subTest(msg="Existing entry"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1002, 101),
                0.3785754120656428
            )

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1002, 103, -3),
                -3
            )

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_element_strain_energy(1002, 103)

    def test_get_group_strain_energy(self) -> None:
        with self.subTest(msg="Existing entry"):
            self.assertEqual(
                self.cdb.beams.get_group_strain_energy(1002, 10),
                0.3785754120656429 + 1.2396276374589636
            )

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.beams.get_group_strain_energy(1002, 11, -3),
                -3
            )

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_group_strain_energy(1002, 11)

    def test_get_strain_energy_after_clear_all(self) -> None:
        self.cdb.beams.clear_all_strain_energy()
        with self.subTest(msg="Check clear all method"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_element_strain_energy(1001, 101)

        self.cdb.beams.calculate_strain_energy(1001)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1001, 101),
                0.029400526651160386
            )


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderBeamStrainEnergyWithDIVTestSuite(TestCase):
    def setUp(self) -> None:
        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "BEAM_STRAIN_ENERGY_WITH_DIV",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.open()
        self.cdb.beams.calculate_strain_energy([1000, 1001, 1002])

    def tearDown(self) -> None:
        self.cdb.close()

    def test_get_strain_energy(self) -> None:
        data = DataFrame(
            _DATA_DIV,
            columns=_COLUMNS
        ).set_index(["LOAD_CASE", "ELEM_ID"], drop=False).sort_index()

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(
            data,
            self.cdb.beams.get_strain_energy(),
            rtol=1E-7
        )

    def test_get_element_strain_energy(self) -> None:
        with self.subTest(msg="Existing entry"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1002, 101),
                0.41403606153995803
            )

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1002, 103, -3),
                -3
            )

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_element_strain_energy(1002, 103)

    def test_get_group_strain_energy(self) -> None:
        with self.subTest(msg="Existing entry"):
            self.assertEqual(
                self.cdb.beams.get_group_strain_energy(1002, 10),
                0.41403606153995803 + 0.8608525260131692
            )

        with self.subTest(msg="Non existing entry with default"):
            self.assertEqual(
                self.cdb.beams.get_group_strain_energy(1002, 11, -3),
                -3
            )

        with self.subTest(msg="Non existing entry without default"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_group_strain_energy(1002, 11)

    def test_get_strain_energy_after_clear_all(self) -> None:
        self.cdb.beams.clear_all_strain_energy()
        with self.subTest(msg="Check clear all method"):
            with self.assertRaises(LookupError):
                self.cdb.beams.get_element_strain_energy(1001, 101)

        self.cdb.beams.calculate_strain_energy(1001)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.beams.get_element_strain_energy(1001, 101),
                0.029400526651160386
            )
