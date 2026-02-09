.. _usage_cdb_reader:

CDB Reader
==========

Methods for loading and accessing data from a CDB file are provided by the
`SOFiSTiKCDBReader` class.

The following minimal example shows how to create a reader instance and use it to load and
access truss data.

.. code-block:: python

    from py_sofistik_utils import SOFiSTiKCDBReader


    if __name__ == "__main__":

        reader = SOFiSTiKCDBReader(
            ".../path/to/cdb/file/",
            "cdb-file-name",
            ".../path/to/dlls/",
            2025
        )

        reader.open()
        reader.truss_data.load()
        reader.close()

        # some post-processing
        initial_length = reader.truss_data.get(100, "L0")
        # ...

Notes
-----

Each instance can manage one single CDB file.