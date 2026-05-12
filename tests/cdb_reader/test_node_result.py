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
        1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        15.0,
        3.75,
        4.590015888214111,
        0.029999999329447746,
        -3.442512035369873,
        2.8125,
        0.0
    ),
    (
        1000,
        12,
        -7.007679960224777e-05,
        -0.0888170599937439,
        -0.01165119931101799,
        -0.04129699617624283,
        0.010226386599242687,
        -0.07887838035821915,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    ),
    (
        1100,
        1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        15.0,
        3.75,
        4.590015888214111,
        0.029999999329447746,
        -3.442512035369873,
        2.8125,
        0.003936484921723604
    ),
    (
        1100,
        12,
        -7.007679960224777e-05,
        -0.0888170599937439,
        -0.01165119931101799,
        -0.03407188504934311,
        0.010226386599242687,
        -0.07887838035821915,
        -0.02336912602186203,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    )
]


@skipUnless(
    all([CDB_PATH, DLL_PATH, VERSION]),
    "SOFiSTiK environment variables not set!"
)
class SOFiSTiKCDBReaderNodeResultsTestSuite(TestCase):
    def setUp(self) -> None:
        self.lcs = [1000, 1100]
        self.node_ids = [1, 12]

        self.cdb = SOFiSTiKCDBReader(
            CDB_PATH,  # type: ignore
            "NODE_RESULTS",
            DLL_PATH,  # type: ignore
            VERSION  # type: ignore
        )
        self.cdb.initialize()
        self.cdb.node.results.load(self.lcs)

        self.data = (
            DataFrame(_DATA, columns=_COLUMNS)
            .set_index(["ID", "LOAD_CASE"], drop=False)
        )

    def tearDown(self) -> None:
        self.cdb.close()

    def test_data(self) -> None:
        assert_frame_equal(self.data, self.cdb.node.results.get_data())

    def test_get_displacements(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "UX"),
                    self.data.UX[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.results.clear(1000)
        self.cdb.node.results.load(1000)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "UY"),
                    self.data.UY[(12, load_case)]
                )

    def test_get_reaction_forces(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "PX"),
                    self.data.PX[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.results.clear_all()
        self.cdb.node.results.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "PY"),
                    self.data.PY[(12, load_case)]
                )

    def test_get_reaction_moments(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "MB"),
                    self.data.MB[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.results.clear_all()
        self.cdb.node.results.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "MZ"),
                    self.data.MZ[(12, load_case)]
                )

    def test_get_rotations(self) -> None:
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "URY"),
                    self.data.URY[(12, load_case)]
                )

        # second run to check pointer rewinding
        self.cdb.node.results.clear_all()
        self.cdb.node.results.load(self.lcs)
        for load_case in self.lcs:
            with self.subTest(load_case=load_case):
                self.assertEqual(
                    self.cdb.node.results.get(12, load_case, "URB"),
                    self.data.URB[(12, load_case)]
                )
