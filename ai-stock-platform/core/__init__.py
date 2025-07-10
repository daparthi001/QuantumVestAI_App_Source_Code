"""Compatibility layer aliasing to api.core."""
import importlib, sys

module = sys.modules.get('api.core')
if module is None:
    module = importlib.import_module('api.core')

sys.modules[__name__] = module
