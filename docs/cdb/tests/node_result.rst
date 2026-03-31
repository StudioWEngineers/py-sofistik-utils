NodeResult
----------

Related test suite: ``test_node_result.py``

Expected CDB file name: ``NODE_RESULTS.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE YC ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 100 TYPE 'IPE' 80 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIR NEGZ GDIV 100

        NODE NO 01 X 0.0 Y 0.0 Z 0.0 FIX F
        NODE NO 12 X 1.5 Y 0.0 Z 0.0
        NODE NO 09 X 5.0 Y 0.0 Z 0.0

        GRP 10 TITL 'BEAM'
            BEAM NO 1 NA 01 NE 12 NCS 100
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 10 TITL 'LOAD PZZ'
            BEAM 1001 TYPE PXX -10.0
            BEAM 1001 TYPE PYY -2.5
            BEAM 1001 TYPE PZZ -3.0
            BEAM 1001 TYPE MXX -0.02
    END

    +PROG ASE
    HEAD LINEAR WARP-0
        SYST PROB LINE
        CTRL WARP 0

        LC 1000 DLZ 1.0 TITL 'LINE-WARP-0'
            LCC 10 FACT 1.0
    END

    +PROG ASE
    HEAD LINEAR WARP-1
        SYST PROB LINE
        CTRL WARP 1

        LC 1100 DLZ 1.0 TITL 'LINE-WARP-1'
        LCC 10 FACT 1.0
    END
