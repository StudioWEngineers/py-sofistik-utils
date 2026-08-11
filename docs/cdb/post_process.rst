.. _post_process:

Post-processing
===============

In addition to providing access to the information contained in a CDB file,
this library provides several post-processing features:

* deflected configurations

Deflected configurations
------------------------

It is often useful to obtain the updated nodal coordinates for a specific
load case.

The updated nodal coordinates :math:`\mathbf{x}` are computed from the
original coordinates :math:`\mathbf{x}_0` and the nodal displacements
:math:`\mathbf{u}` as

.. math::
    \mathbf{x} = \mathbf{x}_0 + \mathbf{u}

where :math:`\mathbf{x}`, :math:`\mathbf{x}_0` and :math:`\mathbf{u}` are
matrices defined in the global coordinate system.

When requesting the coordinates of a node for a load case, the library returns
the deflected coordinates if the node is present in that load case. If the node
is not present in the specific load case, its original (starting) coordinates
are returned instead.
