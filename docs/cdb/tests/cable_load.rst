CableLoad
---------

Related test suite: ``test_cable_load.py``

Expected CDB file name: ``CABLE_LOAD.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
    NORM EN 199X-200X
        STEE 1 S 355 FY 345 FT 470 GAM 78.5 TMAX 40.0 TITL 'S355'
        PROF NO 1 'HEA' 220 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-0-SOF-2025
        SYST 3D GDIV 10 GDIR NEGZ

        LET#COUNT 1
        LOOP#I 4
            LOOP#J 3
                NODE NO #COUNT X 0.0+#I Y 0.0+#J Z 0.0
                LET#COUNT #COUNT+1
            ENDLOOP
        ENDLOOP

        GRP 500 TITL 'CABLES-1'
            CABL NO 1 NA 1 NE 2 NCS 1
            CABL NO 9 NA 2 NE 3 NCS 1

        GRP 501 TITL 'CABLES-2'
            CABL NO 1 NA 7  NE 8  NCS 1
            CABL NO 4 NA 11 NE 12 NCS 1
    END

    +PROG SOFILOAD
    HEAD CABLE LOADS
        LC 1 TITL 'LC-1-PG'
            CABL 5001 TYPE PG PA +1.0 PE -1.0
        LC 2 TITL 'LC-2-PXX'
            CABL GRP 500 TYPE PXX +2.0
        LC 3 TITL 'LC-3-PYY'
            CABL GRP 501 TYPE PYY -3.0
        LC 4 TITL 'LC-4-PZZ'
            CABL 5011 TYPE PZZ -4.0
        LC 5 TITL 'LC-5-PXP'
            CABL GRP 501 TYPE PXP +5.0
        LC 6 TITL 'LC-6-PYP'
            CABL GRP 500 TYPE PYP -6.0
        LC 7 TITL 'LC-6-PZP'
            CABL 5009 TYPE PZP -7.0
        LC 8 TITL 'LC-8-EX'
            CABL 5001 TYPE EX -8.0
            CABL 5014 TYPE EX -8.0
        LC 9 TITL 'LC-9-WX'
            CABL GRP 501 TYPE WX +9.0
        LC 10 TITL 'LC-10-DT'
            CABL GRP 501 TYPE DT -10.0
        LC 11 TITL 'LC-11-VX'
            CABL GRP (500, 501, 1) TYPE VX 11.0
    END
