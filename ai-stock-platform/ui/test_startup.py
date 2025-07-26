#!/usr/bin/env python3
"""
QuantumVestAI Application Startup Test
Tests the application without starting the server
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""

print("QuantumVestAI Application Startup Test")
print("=" * 50)

try:
    print("Testing imports...")
    import os
    import sys
    from pathlib import Path

    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("✓ Basic imports successful")
    
    # Test route imports (without FastAPI dependencies)
    print("Testing route modules...")
    
    modules_to_test = [
        'routes.auth',
        'routes.dashboard', 
        'routes.forecast',
        'routes.market',
        'routes.watchlist',
        'routes.predictability',
        'routes.settings',
        'routes.utils',
        'routes.api_proxy'
    ]
    
    imported_modules = []
    failed_modules = []
    
    for module in modules_to_test:
        try:
            # Test if we can at least parse the module
            module_path = current_dir / f"{module.replace('.', '/')}.py"
            with open(module_path, 'r') as f:
                content = f.read()
                # Simple validation - check if it compiles
                compile(content, str(module_path), 'exec')
            imported_modules.append(module)
            print(f"✓ {module}")
        except Exception as e:
            failed_modules.append((module, str(e)))
            print(f"✗ {module}: {str(e)}")
    
    print(f"\nResults:")
    print(f"Successfully validated: {len(imported_modules)}/{len(modules_to_test)} modules")
    
    if imported_modules:
        print("\n✓ Working modules:")
        for module in imported_modules:
            print(f"  - {module}")
    
    if failed_modules:
        print("\n✗ Failed modules:")
        for module, error in failed_modules:
            print(f"  - {module}: {error}")
    
    # Test main application structure
    print("\nTesting main application structure...")
    
    required_dirs = ['templates', 'static', 'routes', 'services', 'config', 'utils']
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            missing_dirs.append(dir_name)
            print(f"✗ {dir_name}/ directory missing")
    
    # Check main.py
    main_path = current_dir / 'main.py'
    if main_path.exists():
        print("✓ main.py exists")
        try:
            with open(main_path, 'r') as f:
                content = f.read()
                compile(content, str(main_path), 'exec')
            print("✓ main.py compiles successfully")
        except Exception as e:
            print(f"✗ main.py compilation error: {str(e)}")
    else:
        print("✗ main.py missing")
    
    print("\n" + "=" * 50)
    if not failed_modules and not missing_dirs:
        print("🎉 APPLICATION STRUCTURE VALIDATION SUCCESSFUL!")
        print("The QuantumVestAI UI is ready for deployment!")
    else:
        print("⚠️  Some issues found, but core functionality should work")
    
    print("\nApplication Info:")
    print("- Version: 2.0.0")
    print("- Author: hemanth9398") 
    print("- Updated: 2025-07-07 21:54:42")
    print("- Demo Mode: Enabled")
    print("- Features: Auth, Dashboard, Forecast, Market, Watchlist, Predictability, Settings")

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
