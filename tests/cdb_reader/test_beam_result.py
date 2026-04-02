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
    "LOAD_CASE", "GROUP", "ELEM_ID", "POS", "POS_REL",
    "N", "VY", "VZ", "MT", "MY", "MZ", "MB", "MT2"
]
_DATA = [
    [1000, 10, 101, 0.0, 0.0, 141.17791748046875, 0.0, 8.607751846313477, 0.0, -1.4024990946381877e-07, 0.0, 0.0, 0.0],
    [1000, 10, 101, 5.024937629699707, 1.0, 144.605224609375, 0.0, -7.619272232055664, 0.0, 2.5785319805145264, 0.0, 0.0, 0.0],
    [1001, 10, 101, 0.0, 0.0, 97.34918975830078, 1.0547282695770264, 0.5243112444877625, -4.9875807762146, 0.08800704032182693, 0.527148425579071, 0.0, 0.0],
    [1001, 10, 101, 5.024937629699707, 1.0, 97.27648162841797, 1.0547282695770264, -0.20271311700344086, -4.9875807762146, 0.9910196661949158, -4.7727952003479, 0.0, 0.0],
    [1000, 20, 202, 0.0, 0.0, 144.60569763183594, 0.0, -0.09143529832363129, 0.0, 2.5785322189331055, 0.0, 0.0, 0.0],
    [1000, 20, 202, 1.0049874782562256, 0.19999999051058553, 144.58883666992188, 0.0, -0.2601200044155121, 0.0, 1.646203875541687, 0.0, 0.0, 0.0],
    [1000, 20, 202, 2.009974956512451, 0.39999998102117107, 144.57196044921875, 0.0, -0.4288047254085541, 0.0, 1.0253995656967163, 0.0, 0.0, 0.0],
    [1000, 20, 202, 3.014962673187256, 0.6000000189788289, 144.5550994873047, 0.0, -0.5974894762039185, 0.0, 0.6129060387611389, 0.0, 0.0, 0.0],
    [1000, 20, 202, 4.019949913024902, 0.7999999620423421, 144.53822326660156, 0.0, -0.7661741375923157, 0.0, 0.30551064014434814, 0.0, 0.0, 0.0],
    [1000, 20, 202, 5.024937629699707, 1.0, 144.5213623046875, 0.0, -0.9348588585853577, 0.0, 5.246569845240856e-09, 0.0, 0.0, 0.0],
    [1001, 20, 202, 0.0, 0.0, 97.27433013916016, 5.236222743988037, 0.19781945645809174, -4.992882251739502, 1.5245352983474731, -4.712049961090088, 0.0, 0.0],
    [1001, 20, 202, 1.0049874782562256, 0.19999999051058553, 97.25746154785156, 2.7237539291381836, 0.029134752228856087, -3.992882490158081, 1.4633088111877441, -6.626814365386963, 0.0, 0.0],
    [1001, 20, 202, 2.009974956512451, 0.39999998102117107, 97.24059295654297, 0.21128533780574799, -0.13954995572566986, -2.992882490158081, 1.3016397953033447, -7.243962287902832, 0.0, 0.0],
    [1001, 20, 202, 3.014962673187256, 0.6000000189788289, 97.22372436523438, -2.3011839389801025, -0.30823469161987305, -1.9928823709487915, 1.058079481124878, -6.428646564483643, 0.0, 0.0],
    [1001, 20, 202, 4.019949913024902, 0.7999999620423421, 97.20685577392578, -4.813652038574219, -0.47691938281059265, -0.9928827285766602, 0.7511792778968811, -4.046023368835449, 0.0, 0.0],
    [1001, 20, 202, 5.024937629699707, 1.0, 97.18998718261719, -7.3261213302612305, -0.645604133605957, 0.007117461878806353, 0.3994902968406677, 0.03875531628727913, 0.0, 0.0],
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderBeamResultTestSuite(TestCase):
    def setUp(self) -> None:
        self.load_cases = list(range(1000, 1002, 1))

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "BEAM_RESULTS",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.beams.results.load(self.load_cases)

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        data = DataFrame(
            _DATA,
            columns=_COLUMNS
        ).set_index(["ELEM_ID", "LOAD_CASE", "POS_REL"], drop=False)

        # NOTE:
        # Float values loaded from the CDB contain inherent numerical noise.
        # The chosen tolerance is stricter than pandas default and reflects the
        # maximum relative error observed in practice, ensuring stable and
        # reproducible comparisons.
        assert_frame_equal(data, self.cdb.beams.results.data(), rtol=1E-7)

    def test_get(self) -> None:
        with self.subTest(msg="Axial force"):
            self.assertEqual(
                self.cdb.beams.results.get(202, 1001, 0.40),
                97.24059295654297
            )

        with self.subTest(msg="Shear force VY"):
            self.assertEqual(self.cdb.beams.results.get(101, 1000, 1, "VY"), 0)

        with self.subTest(msg="Shear force VZ"):
            self.assertEqual(
                self.cdb.beams.results.get(202, 1000, 0.8, "VZ"),
                -0.7661741375923157
            )

        with self.subTest(msg="Bending moment MY"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MY"),
                0.08800704032182693
            )

        with self.subTest(msg="Bending moment MZ"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MZ"),
                0.527148425579071
            )

        with self.subTest(msg="Torsion"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MT"),
                -4.9875807762146
            )

        with self.subTest(msg="Warping moment MB"):
            self.assertEqual(self.cdb.beams.results.get(101, 1001, 0, "MB"), 0)

        with self.subTest(msg="Secondary torsion moment MT2"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MT2"),
                0
            )

    def test_get_after_clear(self) -> None:
        self.cdb.beams.results.clear(1000)
        with self.subTest(msg="Check clear method"):
            with self.assertRaises(LookupError):
                self.cdb.beams.results.get(202, 1000, 0.8, "VZ")

        self.cdb.beams.results.load(1000)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MT"),
                -4.9875807762146
            )

    def test_get_after_clear_all(self) -> None:
        self.cdb.beams.results.clear_all()
        with self.subTest(msg="Check clear_all method"):
            with self.assertRaises(LookupError):
                self.cdb.beams.results.get(202, 1000, 0.8, "VZ")

        self.cdb.beams.results.load(self.load_cases)
        with self.subTest(msg="Check indexes management"):
            self.assertEqual(
                self.cdb.beams.results.get(101, 1001, 0, "MT"),
                -4.9875807762146
            )

    def test_load_with_duplicated_load_cases(self) -> None:
        self.cdb.beams.results.clear_all()
        self.cdb.beams.results.load(self.load_cases + [1000])
        self.assertEqual(
            self.cdb.beams.results.get(101, 1001, 0, "MT"),
            -4.9875807762146
        )
