#!/bin/bash
# Netlify build script
echo "Building for Netlify..."

# Copy static files
mkdir -p build
cp -r static/* build/ 2>/dev/null || true
cp -r templates/* build/ 2>/dev/null || true

# Copy database files
cp *.db build/ 2>/dev/null || true
cp *.accdb build/ 2>/dev/null || true

echo "Build complete"
