import importlib, sys
module = importlib.import_module('api.core.middleware')
sys.modules[__name__] = module
