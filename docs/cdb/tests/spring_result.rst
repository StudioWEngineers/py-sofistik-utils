SpringResult
------------

Related test suite: ``test_spring_result.py``

Expected CDB file name: ``SPRING_RESULT.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIR NEGZ GDIV 10

        NODE NO 01 X 0.0 Y 0.0 Z 0.0 FIX F
        NODE NO 12 X 1.0 Y 0.0 Z 0.0 FIX F
        NODE NO 09 X 0.0 Y 1.0 Z 0.0 FIX MM

        GRP 10 TITL 'SPRING 1'
            SPRI NO 2 NA 01 NE 09 CP 1.0E2 CT 0.0 CM 0.0
        GRP 11 TITL 'SPRING 2'
            SPRI NO 3 NA 09 NE 12 CP 0.0 CT 1.0E2 CM 1.0E5
    END

    +PROG SOFILOAD
    HEAD LOADS
        LC 10 TITL 'LOAD PXX'
            NODE 9 TYPE PXX +1.0
        LC 11 TITL 'LOAD PYY'
            NODE 9 TYPE PYY +10.0
    END

    +PROG ASE
    HEAD LINEAR
        SYST PROB LINE

        LC 1000 DLZ 0.0
            LCC 10 FACT 1.0
            LCC 11 FACT 1.0
    END
