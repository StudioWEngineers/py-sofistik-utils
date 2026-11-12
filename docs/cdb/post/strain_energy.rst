Strain Energy
-------------

The strain energy can be calculated from the internal forces obtained from
SOFiSTiK, together with the relevant cross-sectional properties and the
element length.

Under the hyphoteses of:

* small displacements and
* constant material and cross-sectional properties of the beam along its length,

the general expression for the strain energy of an elastic beam is:

.. math::
    :label: strain_energy_general

    U = \frac{1}{2} \int_{0}^{L} \left(
            \frac{N^{2}\left(x\right)}{EA} +
            \frac{M_{Y}^{2}\left(x\right)}{EI_{Y}} +
            \frac{M_{Z}^{2}\left(x\right)}{EI_{Z}} +
            \frac{k_{Y}V_{Y}^{2}\left(x\right)}{GA} +
            \frac{k_{Z}V_{Z}^{2}\left(x\right)}{GA} +
            \frac{T^{2}\left(x\right)}{GJ}
        \right) dx

where :math:`N` is the axial force, :math:`M_Y` and :math:`M_Z` are the
bending moments, :math:`V_Y` and :math:`V_Z` are the shear forces, :math:`T` is
the torsional moment, :math:`E` and :math:`G` are the normal and shear moduli,
:math:`A`, :math:`I_Y` and :math:`I_Z` are the area and the two second moments
of area of the cross-section. :math:`k_Y` and :math:`k_Z` are the two shear
factors.

This expression is particularized and further developed for each type of finite
element in the next paraghraps.

.. important::

   The strain energy calculated by this module is approximate only. Further
   details are provided below.

   Although efforts have been made to ensure that the relevant engineering
   theory has been correctly implemented, it remains the user's
   responsibility to verify and validate the results, particularly with
   regard to whether the adopted simplifications are appropriate for the
   intended use.

Beam elements
"""""""""""""

If the contributions of shear forces and torsion can be neglected, the
expression :eq:`strain_energy_general` can be simplified to:

.. math::
    U = \frac{1}{2E} \int_{0}^{L} \left(
            \frac{N^{2}\left(x\right)}{A} +
            \frac{M_{Y}^{2}\left(x\right)}{I_{Y}} +
            \frac{M_{Z}^{2}\left(x\right)}{I_{Z}}
        \right) dx

If we assume a generic linear variation for any of the internal force of the type:

.. math::
    Q(x) = a + bx

Its square integral over the beam length is:

.. math::
    \int_{0}^{L} Q(x)^{2}dx = \frac{L}{3} \left( Q_{1}^{2} + Q_{1}Q_{2}+ Q_{2}^{2}\right)

Where :math:`Q_1` and :math:`Q_2` are the values of :math:`Q` at beam end nodes

Therefore the :

.. math::

   U = \frac{L}{6E} \left[
           \frac{N_{1}^{2} + N_{1}N_{2} + N_{2}^{2}}{A}
           +
           \frac{M_{Y1}^{2} + M_{Y1}M_{Y2} + M_{Y2}^{2}}{I_Y}
           +
           \frac{M_{Z1}^{2} + M_{Z1}M_{Z2} + M_{Z2}^{2}}{I_Z}
       \right]

This equation, which is the one implemented, is valid if the