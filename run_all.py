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


def _spawn(cmd: list[str], name: str, extra_env: dict[str, str] | None = None) -> subprocess.Popen:
    print(f"[start] {name}: {' '.join(cmd)}")
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.Popen(cmd, cwd=BASE_DIR, env=env)


def main() -> int:
    backend_cmd = [sys.executable, "backend/app.py"]
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"]

    backend = _spawn(backend_cmd, "backend", {"AIOPS_DISABLE_RELOADER": "1"})
    time.sleep(1.5)
    dashboard = _spawn(streamlit_cmd, "streamlit")

    processes = [backend, dashboard]
    stopping = False

    def _shutdown(*_: object) -> None:
        nonlocal stopping
        stopping = True
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
                if not stopping:
                    print("[error] backend exited; stopping launcher")
                _shutdown()
                return 1 if not stopping else 0
            if dashboard.poll() is not None:
                if not stopping:
                    print("[error] streamlit exited; stopping launcher")
                _shutdown()
                return 1 if not stopping else 0
            time.sleep(1)
    except KeyboardInterrupt:
        _shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
