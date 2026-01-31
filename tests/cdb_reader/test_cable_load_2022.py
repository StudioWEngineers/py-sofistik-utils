# standard library imports
from os import environ
from os.path import dirname

# third party library imports

# local library specific imports
from py_sofistik_utils.cdb_reader import SOFiSTiKCDBReader
from . test_cable_load_common import SOFiSTiKCDBReaderCableLoadTestSuite as CLTS


DLL_PATH = environ.get("SOFISTIK_DLL_PATH")
print("*********\n")
print(DLL_PATH)
print("*********\n")


class SOFiSTiKCDBReaderCableLoadTestSuite2022(CLTS):
    """Tests for the `SOFiSTiKCDBReader`, `CableLoad` module, SOFiSTiK version 2022.
    """
    def setUp(self) -> None:
        super().setUp()

        # override SOFiSTiK reader and load results
        self._cdb = SOFiSTiKCDBReader(
            dirname(__file__) + "\\_cdb\\" ,
            "CABLE_LOAD",
            DLL_PATH,
            2022
        )
        super()._load_data()

    def test_get_element_load_2022(self) -> None:
        """Tests for the `get_element_load` method.
        """
        self.get_element_load()

    #def test_get_element_load_after_clear_2022(self) -> None:
    #    """Test for the `get_element_load` method after a `clear` call.
    #    """
    #    self.get_element_load_after_clear()

    #def test_get_element_load_after_clear_all_2022(self) -> None:
    #    """Test for the `get_element_load` method after a `clear_all` call.
    #    """
    #    self.get_element_load_after_clear_all()
