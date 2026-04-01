NodeData
--------

Related test suite: ``test_node_data.py``

There are two test suites for nodal data and therefore two expected CDB files.
The first one tests basic data, while the second tests non-contiguous node
numbering as well as unused nodes.

Part I
""""""

Expected CDB file name: ``NODE_DATA.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 100
        LET#COUNT 1
        LOOP#I 4
            LOOP#J 3
                NODE NO #COUNT X 0.0+#I Y 0.0+#J Z 0.0
                LET#COUNT #COUNT+1
            ENDLOOP
        ENDLOOP

        NODE NO 1 FIX PXPYPZ
        NODE NO 2 FIX PXPYPZMX
        NODE NO 3 FIX PYPZMX
        NODE NO 4 FIX PXPYPZ
        NODE NO 5 FIX PXPYPZ
        NODE NO 8 FIX PXPYPZ
        NODE NO 9 FIX F
    END

Part II
"""""""

Expected CDB file name: ``NODE_DATA_NON_CONTIGUOUS_AND_FREE.cdb``

Runs with: SOFiSTiK 2025

Version: 1

.. code-block:: text

    +PROG AQUA
    HEAD MATERIAL
        NORM 'DIN' 'EN199X-200X'
        STEE 1 TYPE S '355'
    END

    +PROG SOFIMSHA
    HEAD GEOMETRY REV-1-SOF-2025
    SYST 3D GDIR NEGZ GDIV 10

        NODE 1 X 0.0 Y 0.0 Z 0.0
        NODE 3 X 1.0 Y 0.0 Z 0.0
        NODE 5 X 1.0 Y 1.0 Z 0.0
        NODE 7 X 0.0 Y 1.0 Z 0.0
        NODE 9 X 0.5 Y 0.5 Z 0.0

        GRP 2 TITL 'QUAD'
            QUAD NO 1 N1 1 N2 3 N3 5 N4 7 MNO 1
    END
