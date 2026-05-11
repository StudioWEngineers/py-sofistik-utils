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
    "LOAD_CASE",
    "ID",
    "UX",
    "UY",
    "UZ",
    "URX",
    "URY",
    "URZ",
    "URB",
    "PX",
    "PY",
    "PZ",
    "MX",
    "MY",
    "MZ",
    "MB"
]
_DATA = [
    (
        1000,
        12,
        -3.783923602895811e-05,
        -0.002827462973073125,
        -0.0023338133469223976,
        -0.09062584489583969,
        0.003167769405990839,
        -0.0036860923282802105,
        0.0,
        2.0099477637813834e-12,
        -1.3489209749195652e-14,
        -2.8199664825478976e-14,
        6.245004513516506e-17,
        -1.226796442210798e-14,
        4.808653475407709e-15,
        0.0
    ),
    (
        1100,
        12,
        -3.839420969597995e-05,
        -0.003061445662751794,
        -0.002275596372783184,
        -0.06965462863445282,
        0.0031669370364397764,
        -0.003880516393110156,
        -0.08241459727287292,
        1.6154189097505878e-11,
        -3.4916514124461173e-13,
        -9.054978988842777e-13,
        -7.625844400394044e-15,
        -5.024869409453459e-13,
        1.3715417690463028e-13,
        -1.8908485888147197e-16
    )
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderNodeResidualsTestSuite(TestCase):
    def setUp(self) -> None:
        self.lcs = [1000, 1100]
        self.node_ids = [12]

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_RESIDUAL",
            DLL_PATH,  # type: ignore
            int(VERSION)  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.node.residuals.load(self.lcs)

        self.data = (
            DataFrame(_DATA, columns=_COLUMNS)
            .set_index(["ID", "LOAD_CASE"], drop=False)
        )

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(self.data, self.cdb.node.residuals.get_data())

    def test_get_displacements(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "UX"),
                    self.data.UX[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.residuals.clear(1000)
        self.cdb.node.residuals.load(1000)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "UY"),
                    self.data.UY[(12, load_case)]
                )

    def test_get_reaction_forces(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "PX"),
                    self.data.PX[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.residuals.clear_all()
        self.cdb.node.residuals.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "PY"),
                    self.data.PY[(12, load_case)]
                )

    def test_get_reaction_moments(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "MB"),
                    self.data.MB[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.residuals.clear_all()
        self.cdb.node.residuals.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "MZ"),
                    self.data.MZ[(12, load_case)]
                )

    def test_get_rotations(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "URY"),
                    self.data.URY[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.residuals.clear_all()
        self.cdb.node.residuals.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.residuals.get(12, load_case, "URB"),
                    self.data.URB[(12, load_case)]
                )
