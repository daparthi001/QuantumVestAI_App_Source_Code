#!/usr/bin/env python3
"""
OpenAPI Specification Validator for QuantumVestAI API
"""

import json
import sys
from pathlib import Path

import yaml


def validate_openapi_spec():
    """Validate the OpenAPI specification file."""
    print("🔍 Validating QuantumVestAI OpenAPI Specification...")
    
    # Check if files exist
    yaml_file = Path("swagger.yaml")
    json_file = Path("swagger.json")
    
    if not yaml_file.exists():
        print("❌ swagger.yaml not found")
        return False
    
    if not json_file.exists():
        print("❌ swagger.json not found")
        return False
    
    # Validate YAML syntax
    try:
        with open(yaml_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        print("✅ YAML syntax is valid")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    
    # Validate JSON syntax
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        print("✅ JSON syntax is valid")
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error: {e}")
        return False
    
    # Check if YAML and JSON contain the same data
    if yaml_data != json_data:
        print("❌ YAML and JSON files contain different data")
        return False
    print("✅ YAML and JSON files are consistent")
    
    # Validate OpenAPI structure
    spec = yaml_data
    
    # Check required OpenAPI fields
    if spec.get('openapi') != '3.0.3':
        print(f"❌ OpenAPI version should be 3.0.3, found: {spec.get('openapi')}")
        return False
    print("✅ OpenAPI version is correct (3.0.3)")
    
    # Check info section
    info = spec.get('info', {})
    required_info_fields = ['title', 'version', 'description']
    for field in required_info_fields:
        if not info.get(field):
            print(f"❌ Missing required info field: {field}")
            return False
    print("✅ Info section is complete")
    
    # Check servers
    servers = spec.get('servers', [])
    if not servers:
        print("❌ No servers defined")
        return False
    print(f"✅ {len(servers)} server(s) defined")
    
    # Check paths
    paths = spec.get('paths', {})
    if not paths:
        print("❌ No paths defined")
        return False
    print(f"✅ {len(paths)} endpoint(s) defined")
    
    # Check components
    components = spec.get('components', {})
    schemas = components.get('schemas', {})
    security_schemes = components.get('securitySchemes', {})
    
    if not schemas:
        print("❌ No schemas defined")
        return False
    print(f"✅ {len(schemas)} schema(s) defined")
    
    if not security_schemes:
        print("❌ No security schemes defined")
        return False
    print(f"✅ {len(security_schemes)} security scheme(s) defined")
    
    # Check tags
    tags = spec.get('tags', [])
    if not tags:
        print("❌ No tags defined")
        return False
    print(f"✅ {len(tags)} tag(s) defined")
    
    # Validate endpoint coverage
    endpoint_categories = {
        'Health': 0,
        'Authentication': 0,
        'User Management': 0,
        'Stocks': 0,
        'Forecasts': 0,
        'Watchlists': 0,
        'Sentiment': 0,
        'Admin': 0,
        'Data': 0,
        'Social Media': 0
    }
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags_list = details.get('tags', [])
                for tag in tags_list:
                    if tag in endpoint_categories:
                        endpoint_categories[tag] += 1
    
    print("\n📊 Endpoint Coverage by Category:")
    total_endpoints = 0
    for category, count in endpoint_categories.items():
        print(f"   {category}: {count} endpoints")
        total_endpoints += count
    
    print(f"\n✅ Total: {total_endpoints} endpoints across {len(endpoint_categories)} categories")
    
    # Check for expected key endpoints
    expected_endpoints = [
        '/api/v1/health',
        '/api/v1/auth/login',
        '/api/v1/auth/register',
        '/api/v1/users/me',
        '/api/v1/stocks/search',
        '/api/v1/stocks/{ticker}',
        '/api/v1/forecast/{ticker}',
        '/api/v1/watchlist',
        '/api/v1/sentiment/{ticker}',
        '/api/social/twitter/sentiment/{symbol}',
        '/api/v1/admin/stats'
    ]
    
    missing_endpoints = []
    for endpoint in expected_endpoints:
        if endpoint not in paths:
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        print(f"❌ Missing expected endpoints: {missing_endpoints}")
        return False
    
    print("✅ All expected key endpoints are present")
    
    print(f"\n🎉 OpenAPI specification validation completed successfully!")
    print(f"📋 Summary:")
    print(f"   - OpenAPI Version: {spec.get('openapi')}")
    print(f"   - API Title: {info.get('title')}")
    print(f"   - API Version: {info.get('version')}")
    print(f"   - Total Endpoints: {total_endpoints}")
    print(f"   - Schemas: {len(schemas)}")
    print(f"   - Tags: {len(tags)}")
    print(f"   - Servers: {len(servers)}")
    
    return True

if __name__ == "__main__":
    success = validate_openapi_spec()
    sys.exit(0 if success else 1)
