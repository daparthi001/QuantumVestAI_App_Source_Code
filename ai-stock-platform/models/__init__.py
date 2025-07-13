import importlib
import sys

module = importlib.import_module('api.models')
sys.modules[__name__] = module
