from importlib.metadata import version as _pkgver

from .ptag import PTag as PTag
from .ptag_series import PTagInterval as PTagInterval
from .ptag_series import PTagSeries as PTagSeries

__all__ = ["PTag", "PTagSeries", "PTagInterval"]

# Package version
try:
    __version__ = _pkgver("civic-transparency-py-ptag-types")
except Exception:
    __version__ = "0.0.0+unknown"
