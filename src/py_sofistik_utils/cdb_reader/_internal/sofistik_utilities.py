"""
SOFiSTiKUtilities
-----------------

The `SOFiSTiKUtilities` module provides functions and helpers to be used that can be used
across all the classes and modules.
"""
# standard library imports

# third party library imports

# local library specific imports


def decode_cdb_status(status: int) -> str:
    """Decode the CDB status according to SOFiHELP - CDBase.

    Parameters
    ----------
    status: int
        The status of the cdb file as obtained from the original SOFiSTiK function
        `sof_cdb_status`.
    """
    value = ""

    if (32 & status) > 0:
        value += "\n\tFile has active locks"

    if (16 & status) > 0:
        value += "\n\tFile has been written"

    if (8 & status) > 0:
        value += "\n\tFile has been read"

    if (4 & status) > 0:
        value += "\n\tFile has ByteSwap"

    if (2 & status) > 0:
        value += "\n\tIndex is connected to file"

    if (1 & status) > 0:
        value += "\n\tCDBase is active"

    return value[value.find("\n") + 1:]

def decode_beam_end_release(itp2: int) -> str:
    """Decode the beam end release conditions for the given beam end.

    Parameters
    ----------
    itp2: int
        Beam end release condition as obtained from key 100/00.
    """
    value = ""

    if (1 & itp2) > 0:
        value += "N"

    if (2 & itp2) > 0:
        value += "VY"

    if (4 & itp2) > 0:
        value += "VZ"

    if (8 & itp2) > 0:
        value += "MT"

    if (16 & itp2) > 0:
        value += "MY"

    if (32 & itp2) > 0:
        value += "MZ"

    if (64 & itp2) > 0:
        value += "MB"

    return value

def decode_nodal_boundary_condition(kfix: int) -> str:
    """Decode the nodal boundary conditions.

    This function is basically the one provided in the SOFiSTiK online documentation, with
    minor modifications to reflect latest changes in Python. Refer to:

    https://docs.sofistik.com/2024/en/cdb_interfaces/python/examples/python_example3.html

    Parameters
    ----------
    kfix: int
        Nodal degrees of freedom as obtained from key 20/00.
    """
    value = "PXPYPZMXMYMZ"

    if (64 & kfix) > 0:
        value = "PXPYPZMXMYMZ"

    if (32 & kfix) > 0:
        value = value.replace("MZ", "")

    if (16 & kfix) > 0:
        value = value.replace("MY", "")

    if (8 & kfix) > 0:
        value = value.replace("MX", "")

    if (4 & kfix) > 0:
        value = value.replace("PZ", "")

    if (2 & kfix) > 0:
        value = value.replace("PY", "")

    if (1 & kfix) > 0:
        value = value.replace("PX", "")

    # Use SOFiSTiK naming convention
    value = value.replace("PXPYPZ", "PP")
    value = value.replace("MXMYMZ", "MM")
    value = value.replace("PYPZ", "XP")
    value = value.replace("PXPZ", "YP")
    value = value.replace("PXPY", "ZP")
    value = value.replace("MYMZ", "XM")
    value = value.replace("MXMZ", "YM")
    value = value.replace("MXMY", "ZM")
    value = value.replace("PPMM", "F")

    if not value:
        return "FREE"

    return value

def get_element_type(element_code: int) -> str:
    """Return the element type according to SOFiSTiK nomenclature.
    Refer to section 018/-2 in SOFiHELP - CDBase.
    """
    match element_code:
        case 20:
            return "NODE"
        case 100:
            return "BEAM"
        case 150:
            return "TRUSS"
        case 160:
            return "CABLE"
        case 170:
            return "SPRING"
        case 180:
            return "EDGE"
        case 190:
            return "PIPE"
        case 200:
            return "QUAD"
        case 300:
            return "BRIC"
        case _:
            raise RuntimeError(f"Unknown element type \"{element_code}\"!")

def long_to_str(long: int) -> str:
    """Convert an `int` (SOFiSTiK returns a `c_long` actually) to a `str`.

    This function is basically the one shipped with SOFiSTiK installation package in the
    example file `decode_encode_py.py`.
    """
    decode = ""

    part_1 = (long & 0xFF000000) // 0x1000000 & 0xFF
    part_2 = (long & 0xFF0000) // 0x10000
    part_3 = (long & 0xFF00) // 0x100
    part_4 = long & 0xFF

    if part_4 != 0:
        decode += chr(part_4)

    if part_3 != 0:
        decode += chr(part_3)

    if part_2 != 0:
        decode += chr(part_2)

    if part_1 != 0:
        decode += chr(part_1)

    return decode
