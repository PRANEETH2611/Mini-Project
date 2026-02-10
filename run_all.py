"""Launch Flask backend API and Streamlit dashboard with one command.

Usage:
    python run_all.py
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _spawn(cmd: list[str], name: str) -> subprocess.Popen:
    print(f"[start] {name}: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=BASE_DIR)


def main() -> int:
    backend_cmd = [sys.executable, "backend/app.py"]
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"]

    backend = _spawn(backend_cmd, "backend")
    time.sleep(1.5)
    dashboard = _spawn(streamlit_cmd, "streamlit")

    processes = [backend, dashboard]

    def _shutdown(*_: object) -> None:
        print("\n[stop] Shutting down services...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        while True:
            if backend.poll() is not None:
                print("[error] backend exited; stopping launcher")
                _shutdown()
                return 1
            if dashboard.poll() is not None:
                print("[error] streamlit exited; stopping launcher")
                _shutdown()
                return 1
            time.sleep(1)
    except KeyboardInterrupt:
        _shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
