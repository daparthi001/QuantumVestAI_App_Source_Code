import re
from pathlib import Path

CONSTANTS_PATH = Path('ai-stock-platform/ui/src/config/constants.ts')
SERVICE_PATH = Path('ai-stock-platform/ui/src/services/api-service.ts')


def extract_endpoints():
    endpoints = []
    text = CONSTANTS_PATH.read_text()
    # Extract API_ENDPOINTS block
    m = re.search(r"API_ENDPOINTS\s*=\s*{(.*?)};", text, re.S)
    if not m:
        return endpoints
    block = m.group(1)
    current_category = None
    for line in block.splitlines():
        line = line.strip()
        cat_match = re.match(r"([A-Z_]+):\s*{", line)
        if cat_match:
            current_category = cat_match.group(1)
            continue
        if line.startswith('},') or line == '},':
            current_category = None
            continue
        item_match = re.match(r"([A-Z_]+):", line)
        if current_category and item_match:
            endpoints.append(f"{current_category}.{item_match.group(1)}")
    return endpoints


def test_all_endpoints_used():
    endpoints = extract_endpoints()
    service_code = SERVICE_PATH.read_text()
    unused = [e for e in endpoints if f"API_ENDPOINTS.{e}" not in service_code]
    assert not unused, f"Unused endpoints: {unused}"
