.. _usage_cdb_reader:

Basic usage
===========

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

Units of Measurement
--------------------

All quantities retrieved from a SOFiSTiK CDB file are stored without
conversion. Therefore, they should be interpreted in their native units,
summarized below for convenience:

* Forces (internal forces, reactions, loads, etc.) are expressed in *kN*
* Moments (internal moments, reactions, loads, etc.) are expressed in *kNm*
* Displacements (nodal displacements, imposed loads, etc.) are expressed in *m*
* Rotations (nodal rotations, etc.) are expressed in *radians*

For additional details, refer to the SOFiSTiK documentation.

Notes
-----

Each instance can manage one single CDB file.