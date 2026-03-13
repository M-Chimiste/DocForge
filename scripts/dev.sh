#!/usr/bin/env bash
set -euo pipefail

# Start DocForge in a dev container using the production Dockerfile.
# Ctrl+C stops and removes the container automatically.

CONTAINER_NAME="docforge-dev"
PORT="${1:-8000}"

cleanup() {
    echo ""
    echo "Stopping container..."
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    echo "Done."
}
trap cleanup EXIT INT TERM

echo "Building DocForge image..."
docker build -t docforge-dev -f Dockerfile . --quiet

echo "Starting container on http://localhost:${PORT}"
echo "Press Ctrl+C to stop."
echo ""

docker run \
    --name "$CONTAINER_NAME" \
    --rm \
    -p "${PORT}:8000" \
    -v docforge-dev-data:/app/data \
    docforge-dev
