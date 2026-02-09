TrussData
---------

Related test suite: ``test_truss_data.py``

Expected CDB file name: ``TRUSS_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE S TITL 'S355'
        PROF NO 1 TYPE CHS 100.0 10.0 MNO 1
        PROF NO 2 TYPE CHS 200.0 10.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 100
        NODE NO 01 X 00.0 Y 0.0 Z +0.0
        NODE NO 02 X 05.0 Y 0.0 Z -0.5
        NODE NO 03 X 10.0 Y 0.0 Z -1.0

        NODE 01 FIX PX,PY,PZ
        NODE 03 FIX PX,PY,PZ

        GRP 10 TITL 'TRUSS 1'
            TRUS NO 1 NA 1 NE 2 NCS 2
        GRP 20 TITL 'TRUSS 2'
            TRUS NO 2 NA 2 NE 3 NCS 1
    END
