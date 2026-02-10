"""Automatic resolution recommendation model for anomaly incidents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ResolutionPlan:
    auto_resolution: str
    resolution_playbook: str
    resolution_confidence: float
    can_auto_execute: bool


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _severity_score(cpu_usage: float, memory_usage: float, response_time: float, anomaly_score: float) -> float:
    cpu_norm = _bounded(cpu_usage / 100.0)
    memory_norm = _bounded(memory_usage / 100.0)
    latency_norm = _bounded(response_time / 3000.0)
    anomaly_norm = _bounded((abs(anomaly_score) + 0.2) / 1.4)
    return _bounded(0.35 * cpu_norm + 0.25 * memory_norm + 0.25 * latency_norm + 0.15 * anomaly_norm)


def recommend_resolution(
    root_cause: str,
    cpu_usage: float,
    memory_usage: float,
    response_time: float,
    anomaly_score: float,
    failure_probability: float,
    anomaly_label: int,
) -> Dict[str, Any]:
    """Generate automatic remediation suggestion for anomaly rows."""
    if anomaly_label != 1 and failure_probability < 0.5:
        return ResolutionPlan(
            auto_resolution="No automated action required",
            resolution_playbook="Observe only; continue normal monitoring.",
            resolution_confidence=0.20,
            can_auto_execute=False,
        ).__dict__

    severity = _severity_score(cpu_usage, memory_usage, response_time, anomaly_score)

    root = (root_cause or "NORMAL").upper()

    if root == "CPU_OVERLOAD":
        plan = ResolutionPlan(
            auto_resolution="Auto-scale compute tier and restart hottest service",
            resolution_playbook="1) Increase replica count by +2; 2) Restart top-CPU pod/service; 3) Rebalance traffic.",
            resolution_confidence=_bounded(0.55 + 0.35 * severity + 0.10 * failure_probability),
            can_auto_execute=severity >= 0.60,
        )
    elif root == "MEMORY_LEAK":
        plan = ResolutionPlan(
            auto_resolution="Roll restart memory-leaking service and cap memory",
            resolution_playbook="1) Trigger rolling restart; 2) Apply memory limit policy; 3) Enable heap diagnostics.",
            resolution_confidence=_bounded(0.58 + 0.30 * severity + 0.12 * failure_probability),
            can_auto_execute=severity >= 0.58,
        )
    elif root == "LATENCY_SPIKE":
        plan = ResolutionPlan(
            auto_resolution="Shift traffic and reset high-latency upstream",
            resolution_playbook="1) Shift 20% traffic to healthy pool; 2) Flush connection pool; 3) Warm cache layer.",
            resolution_confidence=_bounded(0.50 + 0.32 * severity + 0.10 * failure_probability),
            can_auto_execute=severity >= 0.62,
        )
    else:
        plan = ResolutionPlan(
            auto_resolution="Run safe remediation workflow",
            resolution_playbook="1) Capture diagnostics; 2) Restart impacted component; 3) Escalate if no recovery in 5 min.",
            resolution_confidence=_bounded(0.45 + 0.25 * severity + 0.08 * failure_probability),
            can_auto_execute=severity >= 0.68,
        )

    return plan.__dict__
