TrussResult
-----------

Related test suite: ``test_truss_result.py``

Expected CDB file name: ``TRUSS_RESULT.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE S TITL 'S355'
        PROF NO 1 TYPE CHS 100.0 10.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 10
        NODE NO 01 X 0.0 Y 0.0 Z 0.0 FIX PP
        NODE NO 02 X 0.0 Y 1.0 Z 0.0 FIX PP
        NODE NO 03 X 5.0 Y 0.0 Z 0.0 FIX PYPZ
        NODE NO 04 X 5.0 Y 1.0 Z 0.0 FIX PYPZ

        GRP 2 TITL 'TRUSS 1'
            TRUS NO 3 NA 1 NE 3 NCS 1
        GRP 3 TITL 'TRUSS 1'
            TRUS NO 1 NA 4 NE 2 NCS 1
    END

    +PROG SOFILOAD
    HEAD NODAL LOAD
        LC 1 TITL 'LOAD PXX'
            NODE 3 TYPE PXX 150.0
            NODE 4 TYPE PXX 200.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1000 DLZ 0.0 TITL 'LINEAR ANALYSIS'
            LCC 1 FACT 1.0
    END
