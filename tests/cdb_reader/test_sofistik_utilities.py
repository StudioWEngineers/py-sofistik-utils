# standard library imports
from unittest import TestCase

# third party library imports

# local library specific imports
from py_sofistik_utils.cdb_reader._internals.sofistik_utilities import (
    decode_cdb_status,
    decode_nodal_boundary_condition,
    get_element_type,
    long_to_str,
)


class SOFiSTiKUtilitiesTestSuite(TestCase):
    """Tests for the internal helper functions.
    """
    def test_decode_cdb_status(self) -> None:
        """Tests for the `decode_cdb_status` function.
        """
        status_list = [
            "\tCDBase is active",
            "\tIndex is connected to file",
            "\tFile has ByteSwap",
            "\tFile has been read",
            "\tFile has been written",
            "\tFile has active locks"
        ]

        possible_status = [1, 2, 4, 8, 16, 32]

        for index, status in enumerate(possible_status):
            with self.subTest(index = index):
                self.assertEqual(decode_cdb_status(status), status_list[index])

        with self.subTest():
            self.assertEqual(decode_cdb_status(3), status_list[1] + "\n" + status_list[0])

    def test_decode_nodal_boundary_condition(self) -> None:
        """Tests for the `decode_nodal_boundary_condition` function. Results have been
        taken from:

        https://docs.sofistik.com/2024/en/cdb_interfaces/python/examples/python_example3.html
        """
        kfixs = [112, 113, 1151, 1663]
        nodal_bcs = ["PPMX", "XPMX", "FREE", "FREE"]

        for index, kfix in enumerate(kfixs):
            with self.subTest(kfix = kfix):
                self.assertEqual(decode_nodal_boundary_condition(kfix), nodal_bcs[index])

    def test_get_element_type(self) -> None:
        """Tests for the `get_element_type` function.
        Refer to section 018/-2 in SOFiHELP CDBase.
        """
        ids = [20, 100] + list(range(150, 210, 10)) + [300]
        conversion = [ "NODE", "BEAM", "TRUSS", "CABLE",
                       "SPRING", "EDGE", "PIPE", "QUAD", "BRIC"]

        for index, sof_id in enumerate(ids):
            with self.subTest(index = index):
                self.assertEqual(get_element_type(sof_id), conversion[index])

    def test_long_to_str(self) -> None:
        """Test for the `long_to_str` function. Results have been taken from
        `decode_encode_py.py`, shipped along with SOFiSTiK.
        """
        expected_strings = ["ZC  ", "SF  ", "L_T ", "G_3 "]
        long_to_convert = [538985306, 538986067, 542400332, 540237639]

        for index, expected_str in enumerate(expected_strings):
            with self.subTest(index = index):
                self.assertEqual(long_to_str(long_to_convert[index]), expected_str)
