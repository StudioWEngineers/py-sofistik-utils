# standard library imports
from os import environ
from os.path import dirname
from unittest import TestCase

# third party library imports
from pandas import DataFrame, Index
from pandas.testing import assert_frame_equal

# local library specific imports
from py_sofistik_utils.cdb_reader import SOFiSTiKCDBReader


DLL_PATH = environ.get("SOFISTIK_DLL_PATH")


class SOFiSTiKCDBReaderCableLoadTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `CableLoad` module.
    """
    def setUp(self) -> None:
        self._cdb = SOFiSTiKCDBReader(
            dirname(__file__) + "\\_cdb\\" ,
            "CABLE_LOAD",
            DLL_PATH,
            2022
        )

        self._columns = ["LOAD_CASE", "GROUP", "ELEM_ID", "TYPE", "PA", "PE"]
        self._load_cases = [_ for _ in range(1, 12, 1)] + [100]

        self._load_data()

    def tearDown(self) -> None:
        self._cdb.close()

    def test_get_element_load(self) -> None:
        """Test for the `get_element_load` method.
        """
        with self.subTest(msg="LC-1"):
            expected_dataframe = DataFrame(
                [[1, 500, 5001, "PG", 1.0, -1.0]],
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5001, 1, "PG"),
                expected_dataframe
            )

        with self.subTest(msg="LC-2"):
            expected_dataframe = DataFrame(
                [[2, 500, 5001, "PXX", 2.0, 2.0]],
                index=Index([1]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5001, 2, "PXX"),
                expected_dataframe
            )

        with self.subTest(msg="LC-3"):
            expected_dataframe = DataFrame(
                [[3, 501, 5013, "PYY", -3.0, -3.0]],
                index=Index([7]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5013, 3, "PYY"),
                expected_dataframe
            )

        with self.subTest(msg="LC-4"):
            expected_dataframe = DataFrame(
                [[4, 501, 5012, "PZZ", -4.0, -4.0]],
                index=Index([9]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5012, 4, "PZZ"),
                expected_dataframe
            )

        with self.subTest(msg="LC-5"):
            expected_dataframe = DataFrame(
                [[5, 501, 5011, "PXP", 5.0, 5.0]],
                index=Index([10]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5011, 5, "PXP"),
                expected_dataframe
            )

        with self.subTest(msg="LC-6"):
            expected_dataframe = DataFrame(
                [[6, 500, 5002, "PYP", -6.0, -6.0]],
                index=Index([15]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5002, 6, "PYP"),
                expected_dataframe
            )

        with self.subTest(msg="LC-7"):
            expected_dataframe = DataFrame(
                [[7, 500, 5002, "PZP", -7.0, -7.0]],
                index=Index([18]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5002, 7, "PZP"),
                expected_dataframe
            )

        with self.subTest(msg="LC-8"):
            expected_dataframe = DataFrame(
                [[8, 501, 5013, "EX", -0.008, -0.008]],
                index=Index([20]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5013, 8, "EX"),
                expected_dataframe
            )

        with self.subTest(msg="LC-9"):
            expected_dataframe = DataFrame(
                [[9, 501, 5012, "WX", 0.009, 0.009]],
                index=Index([22]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5012, 9, "WX"),
                expected_dataframe
            )

        with self.subTest(msg="LC-10"):
            expected_dataframe = DataFrame(
                [[10, 501, 5014, "DT", -10.0, -10.0]],
                index=Index([28]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5014, 10, "DT"),
                expected_dataframe
            )

        with self.subTest(msg="LC-11"):
            expected_dataframe = DataFrame(
                [[11, 500, 5002, "VX", 11.0, 11.0]],
                index=Index([30]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5002, 11, "VX"),
                expected_dataframe
            )

        with self.subTest(msg="LC-100"):
            expected_dataframe = DataFrame(
                [[100, 500, 5001, "PYP", -6.0, -6.0]],
                index=Index([40]),
                columns=self._columns
            )

            assert_frame_equal(
                self._cdb.cable_load.get_element_load(5001, 100, "PYP"),
                expected_dataframe
            )

    def test_get_element_load_after_clear(self) -> None:
        """Test for the `get_element_load` method after a `clear` call.
        """
        for lc in self._load_cases:
            self._cdb.cable_load.clear(lc)
            self._cdb.cable_load.load(lc)

        self.test_get_element_load()

    def test_get_element_load_after_clear_all(self) -> None:
        """Test for the `get_element_load` method after a `clear_all` call.
        """
        self._cdb.cable_load.clear_all()

        for lc in self._load_cases:
            self._cdb.cable_load.load(lc)

        self.test_get_element_load()

    def _load_data(self) -> None:
        """Open the CDB file and load the cable load data set for each load case.
        """
        self._cdb.initialize()
        for lc in self._load_cases:
            self._cdb.cable_load.load(lc)
