Introduction
============

*py-sofistik-utils* is an open-source Windows-only Python package that provides utilities
for interfacing with the SOFiSTiK finite element analysis (FEA) software.

In particular, it provides classes and data structures to:

* read SOFiSTiK CDB files in read-only mode.
* read, write and manipulate DAT (Teddy) files.

.. important::
    **SOFiSTiK is a registered trademark of SOFiSTiK AG.**

    ``py-sofistik-utils`` is **NOT** affiliated with, endorsed by, or vetted by SOFiSTiK AG.
    It interfaces with proprietary SOFiSTiK DLLs that are **NOT** distributed with this
    repository or the PyPI wheels and must be supplied by the user.

How to cite this project?
-------------------------

Please use the following BibTeX template to cite *py-sofistik-utils*:

.. code-block:: bibtex

    @misc{py-sofistik-utils,
        author = {Studio W Engineers},
        title = {py-sofistik-utils: Python utilities for the SOFiSTiK finite element analysis software},
        year = {2026},
        url = {https://github.com/StudioWEngineers/py-sofistik-utils}
    }

Disclaimer
----------

*py-sofistik-utils* is an open-source set of tools that benefits from the collaboration
of many contributors. While efforts have been made to ensure the implementation is correct,
it remains the user's responsibility to verify and accept the results.

Please refer to the `license <https://github.com/StudioWEngineers/py-sofistik-utils/blob/main/LICENSE>`_
for the terms and conditions of use.

.. toctree::
    :hidden:

    changelog
    faq

.. toctree::
    :caption: Basics
    :hidden:

    installation
    usage

.. toctree::
    :caption: Testing
    :maxdepth: 1
    :hidden:

    cdb/test_setup

.. toctree::
    :caption: API Reference
    :maxdepth: 1
    :hidden:

    cdb/api
