# standard library imports
from sys import version_info
if version_info < (3, 12):
    raise ImportError("py-sofistik-utils does not support Python < 3.12!")

# third party library imports

# local library specific imports
from py_sofistik_utils.cdb_reader import SOFiSTiKCDBReader


__version__ = "0.0.1-dev1"

__all__ = (
    "__version__",
    "SOFiSTiKCDBReader"
)
