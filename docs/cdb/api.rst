.. currentmodule:: py_sofistik_utils.cdb_reader

CDB Reader
==========

This is the API table of contents for the ``SOFiSTiKCDBReader`` class and its helper
classes. Click any class to go to its detailed documentation page.

Public Classes
--------------

Access to CDB files shall be performed via the ``SOFiSTiKCDBReader`` class.

.. autosummary::
    :toctree: ../_autosummary_cdb
    :template: class-template.rst

    SOFiSTiKCDBReader

Private Classes
---------------

All the following classes are internal implementation details of *py-sofistik-utils* and
are intended to be accessed only via the main ``SOFiSTiKCDBReader``. They are exposed in
the documentation solely to provide insight into the underlying data structures and the
associated public API.

.. autosummary::
    :toctree: ../_autosummary_cdb
    :template: class-template.rst

    Beam
    _BeamData
    BeamResults
    _BeamStress
    Cables
    CableData
    CableLoad
    CableResult
    CrossSectionalData
    Groups
    GroupsLC
    _LoadCases
    _Node
    _NodeData
    NodeLoad
    _NodeResult
    _NodeResidual
    Quads
    QuadData
    _SecondaryGroupLCData
    _Spring
    _SpringData
    _SpringResult
    _Truss
    _TrussData
    _TrussLoad
    _TrussResult
