BeamStrainEnergy
----------------

Related test suite: ``test_beam_strain_energy.py``

There are two test suites for beam strain energy and therefore two expected CDB
files. The first one tests usual beam element without internal subdivisions
(DIV), while the second tests beams with subdivisions.

Part I
""""""

Expected CDB file name: ``BEAM_STRAIN_ENERGY.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE S 355 ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 1 TYPE CHS 300.0 10.0 MNO 1
        PROF 2 TYPE CHS 200.0 10.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGY GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0 FIX MX,PX,PY,PZ
        NODE NO 2 X 05.0 Y 0.0 Z +0.0
        NODE NO 3 X 10.0 Y 0.0 Z +0.0 FIX PP

        GRP 10 TITL 'BEAM_DIV'
            BEAM NO 1 NA 1 NE 2 NCS 1 DIV 1 AHIN MT
            BEAM NO 2 NA 2 NE 3 NCS 2.1 EHIN NMYMZ
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 20 TITL 'LOAD-1'
            NODE 2 TYPE PYY -30.0
        LC 30 TITL 'LOAD-2'
            NODE 2 TYPE PXX +150.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1000 DLY 0.0 TITL 'LC 1000'
            LCC 20 FACT 1.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1001 DLY 0.0 TITL 'LC 1001'
            LCC 30 FACT 1.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1002 DLY 0.0 TITL 'LC 1002'
            LCC 20 FACT 1.0
            LCC 30 FACT 1.0
    END

Part II
"""""""

Expected CDB file name: ``BEAM_STRAIN_ENERGY_WITH_DIV.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE S 355 ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 1 TYPE CHS 300.0 10.0 MNO 1
        PROF 2 TYPE CHS 200.0 10.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGY GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0 FIX MX,PX,PY,PZ
        NODE NO 2 X 05.0 Y 0.0 Z +0.0
        NODE NO 3 X 10.0 Y 0.0 Z +0.0 FIX PP

        GRP 10 TITL 'BEAM_DIV'
            BEAM NO 1 NA 1 NE 2 NCS 1 DIV 5 AHIN MT
            BEAM NO 2 NA 2 NE 3 NCS 2.1 EHIN NMYMZ
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 20 TITL 'LOAD-1'
            BEAM 101 TYPE PYY -10.0
        LC 30 TITL 'LOAD-2'
            NODE 2 TYPE PXX +150.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1000 DLY 0.0 TITL 'LC 1000'
            LCC 20 FACT 1.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1001 DLY 0.0 TITL 'LC 1001'
            LCC 30 FACT 1.0
    END

    +PROG ASE
    HEAD LINEAR ANALYSIS
        SYST PROB LINE
        LC 1002 DLY 0.0 TITL 'LC 1002'
            LCC 20 FACT 1.0
            LCC 30 FACT 1.0
    END
