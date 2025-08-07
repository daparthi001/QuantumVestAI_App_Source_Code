# Scripts Directory

This directory contains utility scripts organized by functionality.

## Directory Structure

### `api/`
Contains API-related scripts and fixes:
- `websocket-role-fix.py` - Fixes WebSocket role permission issues

### `ui/`
Contains UI-related JavaScript fixes and updates:
- `market-data-fix.js` - Original market data WebSocket fix
- `market-data-fix-updated.js` - Updated market data WebSocket fix  
- `registration-fix.js` - Registration form fixes

### `deployment/`
Contains deployment and infrastructure scripts:
- Various shell scripts for Kubernetes deployment
- Configuration and setup scripts
- Pod management and update scripts

### `validation/`
Contains validation and testing scripts:
- `validate_api.py` - API validation
- `validate_live_data.py` - Live data validation
- `validate_websocket_fix.py` - WebSocket functionality validation
- `demo_data_source_fix.py` - Data source configuration demo
- `manual_startup_test.py` - Manual startup testing

## Usage

Each subdirectory contains scripts related to specific aspects of the QuantumVestAI application. Scripts maintain their original functionality but are now properly organized for better maintenance and development workflow.