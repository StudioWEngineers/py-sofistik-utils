GroupsLC
--------

Related test suite: ``test_secondary_groups_lc.py``

Expected CDB file name: ``SEC_GROUPS_LC.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE YC ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 1 TYPE CHS 60.0 10.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0 FIX F
        NODE NO 2 X 05.0 Y 0.0 Z -0.5
        NODE NO 3 X 10.0 Y 0.0 Z -1.0 FIX F

        GRP 3 TITL 'GRP 3'
            SPRI NO 2 NA 2 NE 3
            CABL NO 6 NA 1 NE 2 NCS 1
        GRP 10 TITL 'GRP 10'
            BEAM NO 1 NA 1 NE 2 NCS 1
            TRUS NO 1 NA 2 NE 3 NCS 1
        GRP 20 TITL 'GRP 20'
            BEAM NO 2 NA 2 NE 3 NCS 1
            BEAM NO 4 NA 1 NE 2 NCS 1
            CABL NO 6 NA 1 NE 2 NCS 1
    END

    +PROG SOFIMSHA
    HEAD SECONDARY GROUPS
    SYST REST
        GRP 'TEST' TITL 'SECONDARY TEST GROUP'
            BEAM (202,-204)
    END

    +PROG ASE
    HEAD DUMMY ANALYSES
        LOOP#I 2
            SYST PROB LINE
            GRP - VAL YES
            IF (#I==0)
                GRP 10 VAL OFF
                GRP 'TEST' VAL OFF
            ELSE
                GRP 3 VAL OFF
                GRP 'TEST' VAL YES
            ENDIF
            LET#LC #I+1000
            LC #LC DLZ 1.0 TITL 'DUMMY'
            END
        ENDLOOP
    END
