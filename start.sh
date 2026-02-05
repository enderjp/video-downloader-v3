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

echo "[start.sh] Starting uvicorn..."
exec uvicorn main_selenium:app --host 0.0.0.0 --port ${PORT:-8000}
