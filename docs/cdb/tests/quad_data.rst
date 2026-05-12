QuadData
--------

Related test suite: ``test_quad_data.py``

Expected CDB file name: ``QUAD_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
    NORM EN 199X-200X
        STEE 1 S 355 FY 345 FT 470 GAM 78.5 TMAX 40.0 TITL 'S355'
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIV 10 GDIR NEGZ

        NODE NO 1 X 0.0 Y 0.0 Z 0.0
        NODE NO 2 X 1.0 Y 0.0 Z 0.0
        NODE NO 3 X 1.0 Y 1.0 Z 1.0
        NODE NO 4 X 0.0 Y 1.0 Z 0.0

        GRP 5 TITL 'NRA 0'
            QUAD NO 1 N1 1 N2 2 N3 3 N4 4 MNO 1 NRA 0

        GRP 6 TITL 'NRA 1'
            QUAD NO 3 N1 1 N2 2 N3 3 N4 4 MNO 1 NRA 1
            QUAD NO 5 N1 1 N2 2 N3 3 MNO 1 NRA 1

        GRP 8 TITL 'NRA 2'
            QUAD NO 3 N1 1 N2 2 N3 3 N4 4 MNO 1 NRA 2
            QUAD NO 5 N1 1 N2 2 N3 3 MNO 1 NRA 2
    END
