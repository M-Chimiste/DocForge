#!/usr/bin/env bash
set -euo pipefail

# Build frontend
echo "Building frontend..."
cd "$(dirname "$0")/../frontend"
npm ci
npm run build

# Copy built frontend to backend static dir
echo "Bundling frontend into backend..."
rm -rf ../backend/static
cp -r dist ../backend/static

# Build Python package
echo "Building Python package..."
cd ../backend
pip install build
python -m build

echo "Done! Package artifacts in backend/dist/"
