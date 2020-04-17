
import pkgutil

from .analyzer import IPathPropertyAnalysis, IPathValueAnalysis

PROPERTY_ANALYSES = {}
VALUE_ANALYSES = {}


def register_analysis(x):
    if issubclass(x, IPathPropertyAnalysis):
        PROPERTY_ANALYSES[x.name] = x
    elif issubclass(x, IPathValueAnalysis):
        VALUE_ANALYSES[x.name] = x


__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
    __import__(modname)
