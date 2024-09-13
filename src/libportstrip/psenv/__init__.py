"""portstrip environment/psenv"""

from platform import python_version as pyver

__version__: str          = "1.0"    # portstrip version
__regional_version__: str = "1"      # psenv     version
# TODO: Make cache for python version?
__py_version__: str       = pyver()  # python    version

from . import build
from . import shell