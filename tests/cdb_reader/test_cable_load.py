# standard library imports
from os import environ
from os.path import dirname
from unittest import TestCase, skip

# third party library imports
from pandas import DataFrame, Index
from pandas.testing import assert_frame_equal

# local library specific imports
from py_sofistik_utils.cdb_reader import SOFiSTiKCDBReader


DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
SOFISTIK_VERSION = environ.get("SOFISTIK_VERSION")


class SOFiSTiKCDBReaderCableLoadTestSuite(TestCase):
    """Tests for the `SOFiSTiKCDBReader`, `CableLoad` module.
    """
    def setUp(self) -> None:
        if not DLL_PATH:
            self.fail("SOFISTIK_DLL_PATH environment variable is not set")

        if not SOFISTIK_VERSION:
            self.fail("SOFISTIK_VERSION environment variable is not set")

        self._cdb = SOFiSTiKCDBReader(
            dirname(__file__) + "\\_cdb\\" ,
            "CABLE_LOAD",
            DLL_PATH,
            int(SOFISTIK_VERSION)
        )

        self._columns = ["LOAD_CASE", "GROUP", "ELEM_ID", "TYPE", "PA", "PE"]
        self._load_cases = [_ for _ in range(1, 12, 1)] + [100]

        self._load_data()

    def tearDown(self) -> None:
        self._cdb.close()

    def test_get_element_load(self) -> None:
        """Test for the `get_element_load` method.
        """
        self.assertEqual(self._cdb.cable_load.get(5002, 7, "PZP", "PA"), -7.0)

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
        self._cdb.cable_load.load(self._load_cases)
