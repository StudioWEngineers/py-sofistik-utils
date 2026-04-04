BeamData
--------

Related test suite: ``test_beam_data.py``

Expected CDB file name: ``BEAM_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL AND SECTIONS
        NORM EN 199X-200X
        STEE NO 1 TYPE S 355 ES 210000.0 GAM 78.5 TITL 'S355'
        PROF 1 TYPE CHS 100.0 10.0 MNO 1
        PROF 2 TYPE CHS 200.0 8.0 MNO 1
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 10
        NODE NO 1 X 00.0 Y 0.0 Z +0.0 FIX MX,PX,PY,PZ
        NODE NO 2 X 05.0 Y 0.0 Z -0.5
        NODE NO 3 X 10.0 Y 0.0 Z -1.0 FIX PP

        GRP 10 TITL 'BEAM_DIV'
            BEAM NO 1 NA 1 NE 2 NCS 1 DIV 5 AHIN MT
        GRP 20 TITL 'BEAM_TAPERED'
            BEAM NO 2 NA 2 NE 3 NCS 1.2 EHIN NMYMZ
    END
