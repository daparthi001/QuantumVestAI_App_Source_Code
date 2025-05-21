#!/bin/bash

# Remove conflicting logging directory if it exists
rm -rf /app/logging

# Create proper directory structure
mkdir -p /app/core/logger