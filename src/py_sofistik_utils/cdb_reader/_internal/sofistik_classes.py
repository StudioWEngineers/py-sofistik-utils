"""
SOFiSTiKClasses
---------------

The `SOFiSTiKClasses` module stores classes and data structures to be used to get access
and gather data from SOFiSTIK-generated *cdb files.

Basically all the class have been copy-pasted from the original `sofistik_daten.py`,
shipped with the addition of doctrings. Wildcard import of the original file has also been
removed.
"""
# standard library imports
from ctypes import c_float, c_int, Structure

# third party library imports

# local library specific imports


class CBEAM(Structure):           # 100/00:+  Beams
    """This class stores information on all the defined beam elements.
    """
    _fields_ = [
        ('m_nr', c_int),          # beam number
        ('m_node', c_int * 2),    # node number start/end
        ('m_np', c_int),          # prop number
        ('m_dl', c_float),        # [1001] beamlength
        ('m_t', c_float * 3 * 3), # transformation matrix
        ('m_ex', c_float * 2 * 3),# [1001]
        ('m_nref', c_int),        # reference axis
        ('m_spar', c_float * 2),  # distances along a continuous beam or
        ('m_bety', c_float),
        ('m_betz', c_float),
        ('m_ldfy', c_float),
        ('m_ldfz', c_float)       # deformation length factor for vz
    ]


# pylint: disable=C0103
class CBEAM_DL(Structure):        # 101/LC:*  distributed beam loading on reference
    """This class stores information on the beam element applied loads, keys 101/LC.
    """
    _fields_ = [
        ('m_nr', c_int),          #        beamnumber
        ('m_typ', c_int),         #        type of load
        ('m_x', c_float),         # [1001] start point
        ('m_l', c_float),         # [1001] length of load
        ('m_pa', c_float),        #        start value of load
        ('m_pe', c_float),        #        end value of load
        ('m_ya', c_float),        # [1001] eccentr. local y A
        ('m_za', c_float),        # [1001] eccentr. local z A
        ('m_ye', c_float),        # [1001] eccentr. local y E
        ('m_ze', c_float),        # [1001] eccentr. local z E
        ('m_dya', c_float),       #        gradient of eccentricity, local y, start
        ('m_dza', c_float),       #        gradient of eccentricity, local z, start
        ('m_dye', c_float),       #        gradient of eccentricity, local y, end
        ('m_dze', c_float),       #        gradient of eccentricity, local z, end
        ('m_origid', c_int)       #        Identifier of the load origin (e.g., tendon id)
    ]


# pylint: disable=C0103
class CBEAM_FOR(Structure):       # 102/LC:+  Total Beam forces and deformations
    """This class stores information on beam forces and deformations.
    """
    _fields_ = [
        ('m_nr', c_int),          # beamnumber
        ('m_x', c_float),         # [1001] distance from start
        ('m_n', c_float),         # [1101] normal force
        ('m_vy', c_float),        # [1102] y-shear force
        ('m_vz', c_float),        # [1102] z-shear force
        ('m_mt', c_float),        # [1103] torsional moment
        ('m_my', c_float),        # [1104] bending moment My
        ('m_mz', c_float),        # [1104] bending moment Mz
        ('m_mb', c_float),        # [1105] warping moment Mb
        ('m_mt2', c_float),       # [1103] 2nd torsional moment
        ('m_ux', c_float),        # [1003] diplacement local x
        ('m_uy', c_float),        # [1003] diplacement local y
        ('m_uz', c_float),        # [1003] diplacement local z
        ('m_phix', c_float),      # [1004] rotation local x
        ('m_phiy', c_float),      # [1004] rotation local y
        ('m_phiz', c_float),      # [1004] rotation local z
        ('m_phiw', c_float),      # [1005] twisting
        ('m_mt3', c_float),       # [1103] 3rd torsionalmom
        ('m_pa', c_float),        # [1095] axial bedding
        ('m_pt', c_float),        # [1095] transverse bedding
        ('m_pty', c_float),       # [1095] local y component of transverse bedding
        ('m_ptz', c_float),       # [1095] local z component of transverse bedding
        ('m_q1', c_float),        # quaternion component q1
        ('m_q2', c_float),        # quaternion component q2
        ('m_q3', c_float),        # quaternion component q3
        ('m_q0', c_float),        # quaternion component q0
        ('m_uxx', c_float),       # [1003] translation in global X
        ('m_uyy', c_float),       # [1003] translation in global Y
        ('m_uzz', c_float),       # [1003] translation in global Z
        ('m_alph_x', c_float),    # [1003] eas displacement local x
        ('m_beta_x', c_float),    # [1004] eas rotation local x (torsion)
        ('m_beta_y', c_float),    # [1004] eas rotation local y
        ('m_beta_z', c_float),    # [1004] eas rotation local z
        ('m_beta_w', c_float),    # [1005] eas twisting
        ('m_alph2_x', c_float),   # [1003] eas displacement local x
        ('m_beta2_x', c_float),   # [1004] eas rotation local x (torsion)
        ('m_beta2_y', c_float),   # [1004] eas rotation local y
        ('m_beta2_z', c_float),   # [1004] eas rotation local z
        ('m_beta2_w', c_float)    # [1005] eas twisting
    ]


# pylint: disable=C0103
class CBEAM_SCT(Structure):       # 100/00:0  Beams sections
    """This class stores information on all the defined beam sections.
    """
    _fields_ = [
        ('m_id', c_int),          # identifier for sections 0
        ('m_nq', c_int),          # number cross section
        ('m_ityp', c_int),        # Bitcodes
        ('m_itp2', c_int),        # Connection / Hinges for x=0,x=dl
        ('m_x', c_float)          # [1001] sectional abscissa
    ]


# pylint: disable=C0103
class CBEAM_STR(Structure):       # 105/LC:+  Stresses in cross-section of beams
    _fields_ = [
        ('m_nr', c_int),          #        beamnumber
        ('m_mnr', c_int),         #        materialnumber
        ('m_x', c_float),         # [1001] distance from start
        ('m_sigc', c_float),      # [1092] compressive stress
        ('m_sigt', c_float),      # [1092] tensile stress
        ('m_tau', c_float),       # [1092] shear stress
        ('m_sigv', c_float),      # [1092] reference stress
        ('m_si', c_float),        # [1092] main tension stress
        ('m_sii', c_float),       # [1092] main compress stress
        ('m_sigo', c_float),      # [1092] uniaxial stress up
        ('m_sigu', c_float),      # [1092] uniaxial stress down
        ('m_dsig', c_float),      # [1092] sway of normal stress
        ('m_dtau', c_float),      # [1092] sway of shear stress
        ('m_sigw', c_float),      # [1092] stress in weldings
        ('m_vb', c_float),        # [1153] Bond force
        ('m_fak_vv', c_float),    #        shear reduction factor = elastic/nonlinear lever
        ('m_n_part', c_float),    # [1101] normal force in that part of the section
        ('m_sigct', c_float),     # [1092] decompression stress
        ('m_rctrl', c_float),     #        control value of stress/strain description
        ('m_es0', c_float),       #        strain in center of total section
        ('m_esy', c_float),       #        strain gradient in y-direction
        ('m_esz', c_float),       #        strain gradient in z-direction
        ('m_yc', c_float),        # [1011] location of center of partial section
        ('m_zc', c_float),        # [1011] location of center of partial section
        ('m_esw', c_float),       #        factor for unit warping
        ('m_vyf', c_float),       # [1102] shear force
        ('m_vzf', c_float),       # [1102] shear force
        ('m_mtf', c_float),       # [1103] primary torsional moment
        ('m_mt2f', c_float)       # [1103] secondary torsional moment
    ]


class CCABL(Structure):           # 160/00  cable elements
    """This class stores information on all the defined beam sections.
    """
    _fields_ = [
        ('m_nr', c_int),          #        cable number
        ('m_node', c_int * 2),    #        nodenumbers
        ('m_nrq', c_int),         #        cross-section number
        ('m_t', c_float * 3),     #        normal direction
        ('m_dl', c_float),        # [1001] length of cable
        ('m_pre', c_float),       # [1101] prestress
        ('m_gap', c_float),       # [1003] slip of element
        ('m_riss', c_float),      # [1101] max tension force
        ('m_flie', c_float),      # [1101] yielding load
        ('m_nref', c_int)         #        reference axis
    ]


# pylint: disable=C0103
class CCABL_RES(Structure):       # 162/LC:+  results of cables
    """This class stores information on the cable element results.
    """
    _fields_ = [
        ('m_nr', c_int),          #        cablenumber
        ('m_n', c_float),         # [1101] normal force
        ('m_v', c_float),         # [1003] axial displacement
        ('m_vq', c_float),        # [1003] maximum suspension of cable across axis
        ('m_vtx', c_float),       # [1003] suspension of cable, global X-component
        ('m_vty', c_float),       # [1003] suspension of cable, global Y-component
        ('m_vtz', c_float),       # [1003] suspension of cable, global Z-component
        ('m_eps0', c_float),      #        Total induced strain
        ('m_n_m', c_float),       # [1101] average normal force
        ('m_f0', c_float),        # [1003] vertical suspension of cable in load direction
        ('m_l0', c_float),        # [1001] relaxed cable length incl. temp. and prestrain effects
        ('m_lex', c_float),       #        nonlinear effect
        ('m_effs', c_float),      #        effective stiffness factor due to cable sagging
        ('m_damm', c_float * 6)   #        Damage Parameter
    ]


# pylint: disable=C0103
class CCABL_LOA(Structure):       # 161/LC  loads on cables
    """This class stores information on the cable element applied loads.
    """
    _fields_ = [
        ('m_nr', c_int),          #        cable number
        ('m_typ', c_int),         #        type of load
        ('m_pa', c_float),        #        start value of load
        ('m_pe', c_float)         #        end value of load
    ]


class CGRP(Structure):            # 11/00  Primary group data
    """This class stores information on the group data, but only for primary groups.
    """
    _fields_ = [
        ('m_ng', c_int),          #        group-number
        ('m_typ', c_int),         #        element code
        ('m_num', c_int),         #        number of elements of this type
        ('m_min', c_int),         #        minimum element-number of group
        ('m_max', c_int),         #        maximum element-number of group
        ('m_mnr', c_int),         #        material-number of group
        ('m_mbw', c_int),         #        reinforcement material-number of group
        ('m_inf', c_int),         #        Bit-code of group
        ('m_ibb', c_int),         #        construction stage no. BIRTH (0 = instant activation)
        ('m_ibd', c_int),         #        construction stage no. DEATH (0 = infinite lifetime)
        ('m_ibg', c_int),         #        reserved
        ('m_v1', c_float),        #        reserved (formerly: total volume [1008])
        ('m_v2', c_float),        #        reserved (formerly: total mass [1180])
        ('m_v3', c_float),        #        reserved (formerly: total reinforcement weight [1030])
        ('m_v4', c_float),        #        reserved
        ('m_v5', c_float),        #        reserved
        ('m_v6', c_float),        #        reserved
        ('m_v7', c_float),        #        reserved
        ('m_v8', c_float),        #        reserved
        ('m_v9', c_float),        #        reserved
        ('m_v10', c_float),       #        reserved
        ('m_v11', c_float),       #        reserved
        ('m_text', c_int * 17)    #        Designation of Group
    ]


# pylint: disable=C0103
class CGRP_LC(Structure):         # 11/LC  Load case specific group data
    """This class stores information on the load case specific group dat, but only for
    primary groups.
    """
    _fields_ = [
        ('m_ng', c_int),          #        group-number
        ('m_typ', c_int),         #        element code
        ('m_num', c_int),         #        number of elements of this type
        ('m_min', c_int),         #        minimum element-number of group
        ('m_max', c_int),         #        maximum element-number of group
        ('m_mnr', c_int),         #        material-number of group
        ('m_mbw', c_int),         #        reinforcement material-number of group
        ('m_inf', c_int),         #        Bit-code of group
        ('m_faks', c_float),      #        stiffness factor of group (ASE/TALPA)
        ('m_v2', c_float),        #        unused (formerly FAKA: reducing factor of axial bedding for pil
        ('m_v3', c_float),        #        unused (formerly FAKT: reducing factor of transverse bedding
        ('m_v4', c_float),        #        unused
        ('m_v5', c_float),        #        unused
        ('m_v6', c_float),        #        unused
        ('m_etot', c_float),      # [1094] total energy
        ('m_ecom', c_float),      # [1094] compression energy  (unused)
        ('m_edev', c_float),      # [1094] shear energy        (unused)
        ('m_ekin', c_float),      # [1094] kinetic energy      (unused)
        ('m_epot', c_float),      # [1094] potential energy    (unused)
        ('m_edam', c_float),      # [1094] damping energy      (unused)
        ('m_h_gw', c_float),      # [1001] Groundwater level
        ('m_v14', c_float),       #        reserved
        ('m_text', c_int * 17)    #        Designation of Group
    ]


# pylint: disable=C0103
class CLC_CTRL(Structure):        # 12/LC:?  Informations on loadcase LC
    """This class stores information on all the defined load cases. Key 12/LC.
    """
    _fields_ = [
        ('m_kind', c_int),        # type of loadcase
        ('m_ityp', c_int),        # action type (14/ID)
        ('m_theo', c_int),        # first order theory
        ('m_iba', c_int * 2),     # construction stage number of birth & death
        ('m_plc', c_int),         # Primary load case for 2nd order analysis
        ('m_rpar', c_float),      # Timevalue of Load [sec]
        ('m_psi0', c_float),      # factor
        ('m_psi1', c_float),      # combin. factor psi1
        ('m_psi2', c_float),      # combin. factor psi2
        ('m_fact', c_float),      # loadcase factor
        ('m_facx', c_float),      # dead load factor X
        ('m_facy', c_float),      # dead load factor Y
        ('m_facz', c_float),      # dead load factor Z
        ('m_rx', c_float),        # [1151] sum of support reactions PX
        ('m_ry', c_float),        # [1151] sum of support reactions PY
        ('m_rz', c_float),        # [1151] sum of support reactions PZ
        ('m_cri1', c_float),      # 1st eval. criteria
        ('m_cri2', c_float),      # 2nd eval. criteria
        ('m_cri3', c_float),      # 3rd eval. criteria
        ('m_gam1', c_float),      # unfavourable factor
        ('m_gam2', c_float),      # favourable factor
        ('m_name', c_int * 8),    # Generating source
        ('m_rtex', c_int * 17)    # Designation of loadcase
    ]


class CNODE(Structure):           # 20/00  Nodes
    """This class stores information on the nodes.
    """
    _fields_ = [
        ('m_nr', c_int),          # node-number
        ('m_inr', c_int),         # internal node-number
        ('m_kfix', c_int),        # degree of freedoms
        ('m_ncod', c_int),        # additional bit code
        ('m_xyz', c_float * 3)    # [1001] X-Y-Z-ordinates
    ]


# pylint: disable=C0103
class CN_DISP(Structure):         # 24/LC:+  Displacements and support forces of nodes
    """This class stores information on the nodal displacements and support forces.
    """
    _fields_ = [
        ('m_nr', c_int),          # node-number
        ('m_ux', c_float),        # [1003] displacement
        ('m_uy', c_float),        # [1003] displacement
        ('m_uz', c_float),        # [1003] displacement
        ('m_urx', c_float),       # [1004] rotation
        ('m_ury', c_float),       # [1004] rotation
        ('m_urz', c_float),       # [1004] rotation
        ('m_urb', c_float),       # [1005] twisting
        ('m_px', c_float),        # [1151] nodal support
        ('m_py', c_float),        # [1151] nodal support
        ('m_pz', c_float),        # [1151] nodal support
        ('m_mx', c_float),        # [1152] support moment
        ('m_my', c_float),        # [1152] support moment
        ('m_mz', c_float),        # [1152] support moment
        ('m_mb', c_float)         # [1105] warping moment
    ]


# pylint: disable=C0103
class CN_DISPI(Structure):        # 26/LC:+  Displacement increments and residual forces
    """This class stores information on the nodal displacement increments and residual
    forces.
    """
    _fields_ = [
        ('m_nr', c_int),          #        node-number
        ('m_ux', c_float),        # [1003] displacement
        ('m_uy', c_float),        # [1003] displacement
        ('m_uz', c_float),        # [1003] displacement
        ('m_urx', c_float),       # [1004] rotation
        ('m_ury', c_float),       # [1004] rotation
        ('m_urz', c_float),       # [1004] rotation
        ('m_urb', c_float),       # [1005] twisting
        ('m_px', c_float),        # [1151] nodal support
        ('m_py', c_float),        # [1151] nodal support
        ('m_pz', c_float),        # [1151] nodal support
        ('m_mx', c_float),        # [1152] support moment
        ('m_my', c_float),        # [1152] support moment
        ('m_mz', c_float),        # [1152] support moment
        ('m_mb', c_float)         # [1105] warping moment
    ]


class CQUAD(Structure):           # 200/00  QuadElements
    """This class stores information on the geometry and properties of quad elements.
    """
    _fields_ = [
        ('m_nr', c_int),          #        elementnumber
        ('m_node', c_int * 4),    #        nodenumbers
        ('m_mat', c_int),         #        materialnumber
        ('m_mrf', c_int),         #        material Reinf.
        ('m_nra', c_int),         #        type of element
        ('m_det', c_float * 3),   #        Parameter of Jacobi Determinant
        ('m_thick', c_float * 5), # [1010] element thickness
        ('m_cb', c_float),        #        bedding factor
        ('m_cq', c_float),        #        tangential bedding factor
        ('m_t', c_float * 3 * 3), #        transformation matrix
        ('m_ifc1', c_int),        #        identifier of a most adjacent outer boundary
        ('m_dfc1', c_float * 4),  # [1001] distance of the nodes to the boundary IFC1
        ('m_ifc2', c_int),        #        identifier of a most adjacent inner boundary
        ('m_dfc2', c_float * 4)   # [1001] distance of the nodes to the boundary IFC2
    ]


class CSECT(Structure):           # 9/NR:0  SectionalValues (total section)
    """This class stores information on the sectional values for beams (total section).
    """
    _fields_ = [
        ('m_id', c_int),          # Identification
        ('m_mno', c_int),         # Materialnumber of sections
        ('m_mrf', c_int),         # Materialnumber of Reinforcement
        ('m_a', c_float),         # [1012] Area
        ('m_ay', c_float),        # [1012] Sheardeformation area Y
        ('m_az', c_float),        # [1012] Sheardeformation area Z
        ('m_it', c_float),        # [1014] Torsional moment of inertia
        ('m_iy', c_float),        # [1014] Moments of inertia y-y
        ('m_iz', c_float),        # [1014] Moments of inertia z-z
        ('m_iyz', c_float),       # [1014] Moments of inertia y-z
        ('m_ys', c_float),        # [1011] y-Ordinate Center of elasticity
        ('m_zs', c_float),        # [1011] z-Ordinate Center of elasticity
        ('m_ysc', c_float),       # [1011] y-Ordinate of Shear-Center
        ('m_zsc', c_float),       # [1011] z-Ordinate of Shear-Center
        ('m_em', c_float),        # [1090] Elasticity Modulus
        ('m_gm', c_float),        # [1090] Shear Modulus
        ('m_gam', c_float)        # [1091] Nominal weight
    ]


# pylint: disable=C0103
class CSECT_ADD(Structure):       # 9/NR:4  SectionalValuesShear , Temperature
    _fields_ = [
        ('m_id', c_int),
        ('m_stype', c_int),
        ('m_mrf', c_int),         #        Materialnumber of Stirup-Reinforcement
        ('m_at', c_float),        # [ 107] Elongationcoefficient for Temperature
        ('m_ymin', c_float),      # [1011] Minimum Ordinate of section to center ys
        ('m_ymax', c_float),      # [1011] Maximum Ordinate of section to center ys
        ('m_zmin', c_float),      # [1011] Minimum Ordinate of section to center zs
        ('m_zmax', c_float),      # [1011] Maximum Ordinate of section to center zs
        ('m_tmin', c_float),      # [1011] minimum thickness of plates
        ('m_tmax', c_float),      # [1011] maximum thickness of plates
        ('m_wt', c_float),        # [1018] maximum tau for primary Torsion Mtp=1
        ('m_wvy', c_float),       # [1017] maximum tau for Shear Vy=1
        ('m_wvz', c_float),       # [1017] maximum tau for Shear Vz=1
        ('m_wt2', c_float),       # [1018] maximum tau for secondary Torsion Mt2=1
        ('m_ak', c_float),        # [1012] kernel area for Torsion (Bredt)
        ('m_ayz', c_float),       # [1012] Shear deviation area
        ('m_ab', c_float),        # [1012] pure concrete area
        ('m_levy', c_float),      # [1011] minimum lever for cracked shear Vy
        ('m_levz', c_float),      # [1011] minimum lever for cracked shear Vz
        ('m_elvy', c_float),      # [  17] elastic shear flux for Vy = Sy-max/Iz
        ('m_elvz', c_float),      # [  17] elastic shear flux for Vz = Sz-max/Iy
        ('m_ymine', c_float),     # [1011] Minimum Ordinate of effective section
        ('m_ymaxe', c_float),     # [1011] Maximum Ordinate of effective section
        ('m_zmine', c_float),     # [1011] Minimum Ordinate of effective section
        ('m_zmaxe', c_float)      # [1011] Maximum Ordinate of effective section
    ]


class CSPRI(Structure):           # 170/00  Spring-elements
    """This class stores information on spring elements.
    """
    _fields_ = [
        ('m_nr', c_int),          # springnumber
        ('m_node', c_int * 2),    # start nodenumber
        ('m_nrq', c_int),         # Material/section no
        ('m_t', c_float * 3),     # normal direction
        ('m_aref', c_float),      # reference area
        ('m_cp', c_float),        # [1095] spring stiffness
        ('m_cq', c_float),        # [1095] transverse stiff.
        ('m_cm', c_float),        # [1098] torsional stiff.
        ('m_pre', c_float),       # prestress
        ('m_gap', c_float),       # slip/gap of spring
        ('m_riss', c_float),      # max tension force
        ('m_flie', c_float),      # yielding load
        ('m_mue', c_float),       # friction cross
        ('m_coh', c_float),       # cohesion cross
        ('m_dil', c_float),       # dilatancy factor
        ('m_gapq', c_float),      # transverse slip/gap
        ('m_dp', c_float),        # damping constant
        ('m_dq', c_float),        # damping shear
        ('m_dm', c_float),        # damping moment
        ('m_expp', c_float),      # exponent for nonlinear damping dp**expp
        ('m_expq', c_float),      # exponent for nonlinear damping dq**expq
        ('m_expm', c_float),      # exponent for nonlinear damping dm**expm
        ('m_tb', c_float * 3),    # rotational direction
        ('m_nref', c_int)         # additional bit code
    ]


# pylint: disable=C0103
class CSPRI_RES(Structure):       # 170/LC:+  results of spring-elements
    """This class stores information on spring element results.
    """
    _fields_ = [
        ('m_nr', c_int),          # springnumber
        ('m_p', c_float),         # [1151] spring force
        ('m_pt', c_float),        # [1151] spring transforce
        ('m_ptx', c_float),       # [1151] global X-shear component
        ('m_pty', c_float),       # [1151] global Y-shear component
        ('m_ptz', c_float),       # [1151] global Z-shear component
        ('m_m', c_float),         # [1152] spring moment
        ('m_v', c_float),         # [1003] axial displacement
        ('m_vt', c_float),        # [1003] trans. displacement
        ('m_vtx', c_float),       # [1003] trans. displacement, global X-component
        ('m_vty', c_float),       # [1003] trans. displacement, global Y-component
        ('m_vtz', c_float),       # [1003] trans. displacement, global Z-component
        ('m_phi', c_float),       # [1004] rotation
        ('m_lex', c_float),       # nonlinear effect
        ('m_stvp', c_float * 10), # State variable / Damage Parameter for CP
        ('m_stvm', c_float * 10), # State variable / Damage Parameter for CM
        ('m_stvt', c_float * 10)  # State variable / Damage Parameter for CT
    ]


class CSYST(Structure):           # 10/00  SystemInfo
    """This class stores general information on the system.
    """
    _fields_ = [
        ('m_iprob', c_int),         # Type of System
        ('m_iachs', c_int),         # Orientation of gravity
        ('m_nknot', c_int),         # Number of nodes
        ('m_mknot', c_int),         # Highest node number
        ('m_igdiv', c_int),         # Group divisor
        ('m_igres', c_int),
        ('m_box', c_float * 2 * 3), # [1001] bounding box
        ('m_tg', c_float * 4 * 3),  # global CDB-System transformation matrix
        ('m_txt', c_int * 64)       # Name of projekt, 127 chars
    ]


class CTRUS(Structure):           # 150/00  truss elements
    """This class stores information on all the truss elements.
    """
    _fields_ = [
        ('m_nr', c_int),          #        truss number
        ('m_node', c_int * 2),    #        nodenumbers
        ('m_nrq', c_int),         #        cross-section number
        ('m_t', c_float * 3),     #        normal direction
        ('m_dl', c_float),        # [1001] length of truss
        ('m_pre', c_float),       # [1101] prestress
        ('m_gap', c_float),       # [1003] slip of element
        ('m_riss', c_float),      # [1101] max tension force
        ('m_flie', c_float),      # [1101] yielding load
        ('m_nref', c_int)         #        reference axis
    ]


# pylint: disable=C0103
class CTRUS_LOA(Structure):       # 151/LC  Loads on truss elements
    """This class stores information on the truss element applied loads.
    """
    _fields_ = [
        ('m_nr', c_int),          #        truss number
        ('m_typ', c_int),         #        type of load
        ('m_pa', c_float),        #        start value of load
        ('m_pe', c_float)         #        end value of load
    ]


# pylint: disable=C0103
class CTRUS_RES(Structure):       # 152/LC:+  results of truss elements
    """This class stores information on truss element results.
    """
    _fields_ = [
        ('m_nr', c_int),          #        truss number
        ('m_n', c_float),         # [1101] normal force
        ('m_v', c_float),         # [1003] axial displacement
        ('m_lex', c_float),       #        nonlinear effect
        ('m_damm', c_float * 6)   #        Damage Parameter
    ]