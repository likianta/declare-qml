from .components import *

# note that we delete Application from `.qt_widgets`, becase we would like to
# use `..application.Application` instead.
del Application

from .application import Application

__version__ = '0.1.0'
