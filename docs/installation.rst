.. _installation:

Installation
============

This project is hosted at `StudioWEngineers/py-sofistik-utils
<https://github.com/StudioWEngineers/py-sofistik-utils>`_ on GitHub. These instructions
will get you a copy of *py-sofistik-utils* up and running on your machine.

Prerequisites
-------------

Python
~~~~~~
- Python 3.12 or newer
- pip (latest version recommended)

The following Python packages are required and will be installed automatically via pip:

- `pandas <https://pandas.pydata.org/>`_ 3.0 or newer
- `numpy <https://numpy.org/>`_ 2.2 or newer

SOFiSTiK
~~~~~~~~
For the use of the ``cdb_reader`` module only, the following SOFiSTiK dynamic libraries
must be available at runtime:

- ``sof_cdb_w-202X.dll`` where ``X`` is year version of the software
- ``libifcoremd.dll``
- ``libmmd.dll``

These three DLLs must be located in the same directory and that directory must be accessible
to Python at runtime. Refer to section :ref:`usage <usage_cdb_reader>` for details.
They are automatically installed with SOFiSTiK and are usually located in the following folders:

- ``...\SOFiSTiK\202X\SOFiSTiK 202X\interfaces\64bit\``
- ``...\SOFiSTiK\202X\SOFiSTiK 202X\``

Again, ``X`` denotes the SOFiSTiK year version.

Currently, the supported SOFiSTiK versions are: 2022, 2023, 2024, and 2025.

Installing via pip (recommended)
--------------------------------

Run the following command to install the latest released version from
`PyPI <https://pypi.org/>`_:

.. code-block:: bash

    python -m pip install py-sofistik-utils

To verify the installation:

.. code-block:: bash

    python -c "import py_sofistik_utils; print(py_sofistik_utils.__version__)"

Editable (development) installation
-----------------------------------

If you want to contribute to the project or modify the source code locally,
install the package in editable mode.

First, clone the repository:

.. code-block:: bash

    git clone https://github.com/StudioWEngineers/py-sofistik-utils.git

Then install the package in editable mode:

.. code-block:: bash

    cd py-sofistik-utils
    python -m pip install -e .
