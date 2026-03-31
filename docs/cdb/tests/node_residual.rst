NodeResidual
------------

Related test suite: ``test_node_residual.py``

Expected CDB file name: ``NODE_RESIDUAL.cdb``

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
            SYST 3D GDIR NEGZ GDIV 10

        NODE NO 01 X 0.0 Y 0.0 Z 0.0 FIX F
        NODE NO 12 X 1.0 Y 0.0 Z 0.0
        NODE NO 09 X 5.0 Y 0.0 Z 0.0

        GRP 10 TITL 'BEAM'
            BEAM NO 1 NA 01 NE 12 NCS 100
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 10 TITL 'LOAD PZZ'
            BEAM 101 TYPE PXX -10.0
            BEAM 101 TYPE PYY -0.5
            BEAM 101 TYPE PZZ -3.0
            BEAM 101 TYPE MXX -0.1
    END

    +PROG TEMPLATE
    HEAD VARIABLES
        STO#TOLERANCE 1E-12
    END

    +PROG ASE
    HEAD TH3 WARP-0
        SYST PROB TH3 ITER 100000 TOL #TOLERANCE
        CTRL SOLV 4
        CTRL WARP 0

        LC 1000 DLZ 1.0 TITL 'TH3-WARP-0'
            LCC 10 FACT 1.0
    END

    +PROG ASE
    HEAD TH3 WARP-1
        SYST PROB TH3 ITER 100000 TOL #TOLERANCE
        CTRL SOLV 4
        CTRL WARP 1

        LC 1100 DLZ 1.0 TITL 'TH3-WARP-1'
            LCC 10 FACT 1.0
    END
