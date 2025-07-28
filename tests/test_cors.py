import os
import importlib

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
os.sys.path.append(ROOT)
os.sys.path.append(os.path.join(ROOT, "api"))

from api.core.middleware import cors


def test_is_origin_allowed_without_header_in_dev():
    os.environ['ENVIRONMENT'] = 'development'
    importlib.reload(cors)
    assert cors.is_origin_allowed(None) is True

