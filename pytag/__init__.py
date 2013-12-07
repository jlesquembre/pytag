import pkg_resources

__version__ = pkg_resources.get_distribution('pytag').version


# high level interface
from pytag.interface import (Audio, AudioReader,       # flake8: noqa
                             FormatNotSupportedError)
