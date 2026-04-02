BeamResult
----------

Related test suite: ``test_beam_result.py``

Expected CDB file name: ``BEAM_RESULTS.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE YC ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 1 TYPE CHS 60.0 10.0 MNO 1
        PROF 2 TYPE CHS 120.0 6.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIR NEGZ GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0 FIX MX,PX,PY,PZ
        NODE NO 2 X 05.0 Y 0.0 Z -0.5
        NODE NO 3 X 10.0 Y 0.0 Z -1.0 FIX PP

        GRP 10 TITL 'BEAM-1'
            BEAM NO 1 NA 1 NE 2 NCS 1.2
        GRP 20 TITL 'BEAM-2'
            BEAM NO 2 NA 2 NE 3 NCS 2 DIV 5
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 11 TITL 'LOADS ZZ'
            BEAM 101 TYPE PZZ -3.0
            BEAM 101 TYPE PXX -1.0
        LC 12 TITL 'LOADS YY'
            BEAM 202 TYPE PYY -2.5
            BEAM 202 TYPE MXX -1.0
    END

    +PROG TEMPLATE
    HEAD BASE VARIABLES
        STO#TOLERANCE 0.000000000000000001
    END

    +PROG ASE
    HEAD
        LOOP#I 2
            SYST PROB TH3 ITER 250 TOL #TOLERANCE
            CTRL OPT ITER VAL 3 V2 1
            LET#LC #I+1000
            LC #LC DLZ 1.0 TITL 'SW + LC-#I'
            LCC #I+11 FACT 1.0
            END
        ENDLOOP
    END
