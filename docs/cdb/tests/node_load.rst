NodeLoad
--------

Related test suite: ``test_node_load.py``

Expected CDB file name: ``NODE_LOADS.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0
        NODE NO 2 X 05.0 Y 0.0 Z -0.5
        NODE NO 3 X 10.0 Y 0.0 Z -1.0
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 10 TITL 'SINGLE LOADS'
            NODE 1 TYPE PZZ -3.0
            NODE 3 TYPE PXX +1.0
        LC 20 TITL 'REPEATED LOADS'
            NODE 2 TYPE PYY -2.5
            NODE 2 TYPE PYY -1.0
            NODE 3 TYPE MYY -1.0
    END
