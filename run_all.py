"""Launch Flask backend, Streamlit dashboard, and optional live simulator.

Usage:
    python run_all.py
    python run_all.py --simulate
    python run_all.py --simulate --fresh-stream
"""
from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Run backend + dashboard with optional live metrics simulation")
    parser.add_argument("--simulate", action="store_true", help="Start the live cloud metrics simulator")
    parser.add_argument("--fresh-stream", action="store_true", help="Start backend with empty dataset so simulator fills it live")
    args = parser.parse_args()

    backend_cmd = [sys.executable, "backend/app.py"]
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"]
    simulator_cmd = [sys.executable, "scripts/cloud_metrics_simulator.py"]

    backend_env = {"AIOPS_DISABLE_RELOADER": "1"}
    if args.fresh_stream:
        backend_env["AIOPS_START_EMPTY"] = "1"

    backend = _spawn(backend_cmd, "backend", backend_env)
    time.sleep(1.5)
    dashboard = _spawn(streamlit_cmd, "streamlit")

    processes = [backend, dashboard]

    if args.simulate:
        time.sleep(1.5)
        simulator = _spawn(simulator_cmd, "simulator")
        processes.append(simulator)

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
            for proc, name in zip(processes, ["backend", "streamlit", "simulator"][: len(processes)]):
                if proc.poll() is not None:
                    if not stopping:
                        print(f"[error] {name} exited; stopping launcher")
                    _shutdown()
                    return 1 if not stopping else 0
            time.sleep(1)
    except KeyboardInterrupt:
        _shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
