#!/bin/sh
set -e

echo "[start.sh] Installing chromedriver via webdriver-manager (if possible)..."
python - <<'PY'
import sys
from webdriver_manager.chrome import ChromeDriverManager
try:
    from webdriver_manager.core.utils import ChromeType
except Exception:
    try:
        from webdriver_manager.utils import ChromeType
    except Exception:
        ChromeType = None

driver_path = None
try:
    if ChromeType is not None:
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    else:
        try:
            driver_path = ChromeDriverManager(chrome_type='chromium').install()
        except Exception:
            driver_path = ChromeDriverManager().install()
except Exception as e:
    print("webdriver-manager install failed:", e)
    sys.exit(0)

print("CHROMEDRIVER_INSTALLED:" + str(driver_path))
PY

echo "[start.sh] Checking for Chromium/Chrome binary..."
if [ -n "${CHROME_BIN}" ]; then
    echo "CHROME_BIN is set: ${CHROME_BIN}"
elif command -v chromium >/dev/null 2>&1; then
    echo "Found chromium in PATH"
elif command -v google-chrome >/dev/null 2>&1; then
    echo "Found google-chrome in PATH"
else
    echo "No Chrome/Chromium binary found. Attempting apt-get install if available and running as root..."
    if command -v apt-get >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
        echo "Installing chromium via apt-get..."
        apt-get update && apt-get install -y chromium
    else
        echo "Cannot install chromium automatically. If deploying to a managed service (Render), either:"
        echo " - Use Docker image that includes Chromium, or"
        echo " - Install Chromium via the platform build steps, or"
        echo " - Switch to Playwright which downloads browsers during build (pip install playwright && playwright install)."
    fi
fi

echo "[start.sh] Starting uvicorn..."
exec uvicorn main_selenium:app --host 0.0.0.0 --port ${PORT:-8000}
