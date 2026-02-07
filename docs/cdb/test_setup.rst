.. _cdb_testing:

CDB Reader
==========

This section explains how to run the test suite locally.

The SOFiSTiK DLLs and CDB files required for the library’s continuous integration
(GitHub Actions) are not included in this repository. Instead, they are fetched
on the fly from private repositories.

Users who wish to contribute must run the test suite locally before submitting a pull
request, in order to verify the impact of their proposed changes. To do so, the required
CDB files must be generated using a proprietary SOFiSTiK license, based on the source
files provided in this section.

.. note::
    All SOFiSTiK source files contained in the following subsections are **not** subject
    to semantic versioning. The version number of each source file is stated on its
    respective page. Any *py-sofistik-utils* release that does not explicitly mention a
    version change in the changelog inherits the version of the preceding release.

Folder structure
----------------

The following folder structure is used by the author locally and in GitHub Actions.
Adopting this structure is recommended but not mandatory.

.. code-block:: text

    py-sofistik-utils-testing/
    ├── DLLs
    │   └── 2022/
    │   |   ├── sof_cdb_w-2022.dll
    │   |   ├── libifcoremd.dll
    │   |   └── libmmd.dll
    │   └── 2023/
    │   |   ├── sof_cdb_w-2023.dll
    │   |   ├── libifcoremd.dll
    │   |   └── libmmd.dll
    │   └── ... all other SOFiSTiK versions of interest
    └── CDBs/
        ├── CABLE_LOAD.cdb
        └── ... all other required CDB files

.. important::
    All CDB files required for testing must be located in the same directory in order to
    be discovered by the test suite. Similarly, all required SOFiSTiK DLLs for a given
    version must be located in the same directory.

Environment variables
---------------------

The test suite expects the following environment variables to be defined:

- ``SOFISTIK_CDB_PATH``: absolute path to the directory containing the required CDB files
- ``SOFISTIK_DLL_PATH``: absolute path to the directory containing the required DLL files
- ``SOFISTIK_VERSION``: SOFiSTiK version used to run the tests

Since these values depend on the SOFiSTiK version being tested, it is recommended to set
these variables temporarily, just for the duration of the test run, rather than adding
them permanently to the user environment.

Running the tests on Windows (MinGW-w64)
----------------------------------------

Using the folder structure described above, SOFiSTiK version 2023 as a reference, and
the temporary environment variable approach, open an MSYS2 MINGW64 shell, navigate to the
``py-sofistik-utils/tests/`` directory, and execute the following command::

    SOFISTIK_CDB_PATH="path/to/py-sofistik-utils-testing/CDBs/" \
    SOFISTIK_DLL_PATH="path/to/py-sofistik-utils-testing/DLLs/2023/" \
    SOFISTIK_VERSION="2023" \
    py -m unittest discover

.. note::
    Based on experience using this library in production with multiple SOFiSTiK versions,
    the provided DLL files have proven to be stable across releases. As a result, it is
    generally sufficient to run the test suite only against the latest available version.

.. toctree::
    :maxdepth: 1
    :hidden:

    tests/cable_load

