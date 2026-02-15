SpringData
----------

Related test suite: ``test_spring_data.py``

Expected CDB file name: ``SPRING_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG SOFIMSHA
        HEAD GEOMETRY REV-1-SOF-2025
        SYST 3D GDIR NEGZ GDIV 100
        NODE NO 01 X 00.0 Y 0.0 Z +0.0
        NODE NO 02 X 05.0 Y 0.0 Z -0.5
        NODE NO 03 X 10.0 Y 0.0 Z -1.0

        GRP 10 TITL 'GRP 1'
            SPRI NO 1 NA 1 NE 2 CP 1.0 CT 2.5
        GRP 20 TITL 'GRP 2'
            SPRI NO 20 NA 2 DX 0.2 DY 0.3 DZ 1.0 CM 1.5
    END
