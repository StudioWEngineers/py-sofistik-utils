CableData
---------

Related test suite: ``test_cable_data.py``

Expected CDB file name: ``CABLE_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
    NORM EN 199X-200X
        STEE 1 S 355 FY 345 FT 470 GAM 78.5 TMAX 40.0 TITL 'S355'
        PROF NO 3 'HEA' 220 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIV 10 GDIR NEGZ

        NODE NO 1 X 0.0 Y 0.0 Z 0.0
        NODE NO 2 X 1.0 Y 1.0 Z 1.0
        NODE NO 5 X 0.0 Y 0.0 Z 1.0

        GRP 50 TITL 'CABLE'
            CABL NO 2 NA 1 NE 2 NCS 3
            CABL NO 5 NA 1 NE 5 NCS 3
    END
