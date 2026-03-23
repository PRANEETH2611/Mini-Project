"""Realistic cloud metrics simulator for live dashboard streaming.

Usage:
    python scripts/cloud_metrics_simulator.py
    python scripts/cloud_metrics_simulator.py --once
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
import math
import random
import time
from urllib import request, error

API_URL = "http://127.0.0.1:5000/api/ingest"


@dataclass
class SimulatorState:
    tick: int = 0
    phase: str = "NORMAL"
    phase_ticks_remaining: int = 25
    cpu_prev: float = 42.0
    mem_prev: float = 3.8
    latency_prev: float = 180.0
    error_prev: int = 0


PHASE_SEQUENCE = [
    ("NORMAL", 28),
    ("CPU_OVERLOAD", 12),
    ("NORMAL", 18),
    ("MEMORY_LEAK", 14),
    ("NORMAL", 18),
    ("LATENCY_SPIKE", 10),
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def next_phase(state: SimulatorState) -> None:
    cycle_index = (state.tick // 20) % len(PHASE_SEQUENCE)
    state.phase, state.phase_ticks_remaining = PHASE_SEQUENCE[cycle_index]


def smooth(previous: float, target: float, noise: float, alpha: float = 0.35) -> float:
    value = previous + alpha * (target - previous) + random.uniform(-noise, noise)
    return value


def generate_metric(state: SimulatorState) -> dict[str, float | int | str]:
    if state.phase_ticks_remaining <= 0:
        next_phase(state)

    state.tick += 1
    state.phase_ticks_remaining -= 1
    wave = math.sin(state.tick / 6.0)

    if state.phase == "CPU_OVERLOAD":
        cpu_target = 89 + wave * 5
        mem_target = 5.6 + wave * 0.4
        latency_target = 820 + wave * 80
        error_target = 7
    elif state.phase == "MEMORY_LEAK":
        cpu_target = 66 + wave * 4
        mem_target = 8.9 + wave * 0.6
        latency_target = 560 + wave * 70
        error_target = 10
    elif state.phase == "LATENCY_SPIKE":
        cpu_target = 58 + wave * 3
        mem_target = 4.8 + wave * 0.3
        latency_target = 2100 + wave * 250
        error_target = 12
    else:
        cpu_target = 43 + wave * 6
        mem_target = 3.9 + wave * 0.5
        latency_target = 210 + wave * 35
        error_target = 1

    state.cpu_prev = clamp(smooth(state.cpu_prev, cpu_target, 2.2), 5, 100)
    state.mem_prev = clamp(smooth(state.mem_prev, mem_target, 0.18), 1.5, 12)
    state.latency_prev = clamp(smooth(state.latency_prev, latency_target, 35), 40, 4000)
    state.error_prev = int(clamp(round(state.error_prev + 0.4 * (error_target - state.error_prev) + random.uniform(-1, 1)), 0, 50))

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_usage": round(state.cpu_prev, 2),
        "memory_usage": round(state.mem_prev, 2),
        "response_time": round(state.latency_prev, 2),
        "error_count": state.error_prev,
    }


def post_metric(api_url: str, payload: dict[str, float | int | str]) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(api_url, data=body, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stream realistic cloud metrics to the backend API")
    parser.add_argument("--api-url", default=API_URL)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    state = SimulatorState()
    next_phase(state)

    print(f"🚀 Streaming simulated cloud metrics to {args.api_url}")
    print("Press Ctrl+C to stop.")

    while True:
        payload = generate_metric(state)
        try:
            status, body = post_metric(args.api_url, payload)
            print(
                f"[{payload['timestamp']}] phase={state.phase:<14} CPU={payload['cpu_usage']:>6}% "
                f"MEM={payload['memory_usage']:>4}GB LAT={payload['response_time']:>7}ms "
                f"ERR={payload['error_count']:>2} status={status}"
            )
            if status >= 400:
                print(body)
        except Exception as exc:
            print(f"❌ Failed to push simulated metrics: {exc}")

        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
