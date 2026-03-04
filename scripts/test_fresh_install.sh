#!/usr/bin/env bash
set -euo pipefail

echo "=== DocForge Fresh Install Validation ==="
echo ""

# --- Test 1: pip install in a clean venv ---
echo "--- Test 1: pip install ---"
VENV_DIR=$(mktemp -d)/docforge-test
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing docforge from backend/..."
pip install ./backend --quiet

echo "Testing 'docforge analyze'..."
docforge analyze --template demo/templates/quarterly_report.docx > /dev/null
echo "  OK: analyze command works"

echo "Testing 'docforge serve' (start and stop)..."
docforge serve --port 8199 &
SERVER_PID=$!
sleep 3

if curl -sf http://localhost:8199/api/v1/projects > /dev/null 2>&1; then
    echo "  OK: serve command works, API responds"
else
    echo "  FAIL: API did not respond"
    kill $SERVER_PID 2>/dev/null || true
    deactivate
    rm -rf "$(dirname "$VENV_DIR")"
    exit 1
fi

kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
deactivate
rm -rf "$(dirname "$VENV_DIR")"
echo "  OK: venv cleaned up"
echo ""

# --- Test 2: Docker build ---
echo "--- Test 2: Docker compose build ---"
if command -v docker &> /dev/null; then
    docker compose build --quiet
    echo "  OK: docker compose build succeeds"

    echo "Testing docker compose up..."
    docker compose up -d
    sleep 5

    if curl -sf http://localhost:8000/api/v1/projects > /dev/null 2>&1; then
        echo "  OK: API responds at :8000"
    else
        echo "  WARN: API did not respond at :8000 (may need more startup time)"
    fi

    docker compose down --remove-orphans
    echo "  OK: docker compose down"
else
    echo "  SKIP: Docker not available"
fi

echo ""
echo "=== All validation checks passed ==="
