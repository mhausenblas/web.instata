# -*- coding: UTF-8 -*-
"""
The RDFExtras namespace package.
"""

__author__ = "Niklas Lindström"
__version__ = "0.1"

# This is a namespace package.
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

