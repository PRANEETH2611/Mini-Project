"""Automatic resolution recommendation model for anomaly incidents."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any
import math


@dataclass(frozen=True)
class ResolutionPlan:
    auto_resolution: str
    resolution_playbook: str
    resolution_confidence: float
    can_auto_execute: bool
    resolution_status: str
    resolution_alert: str


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        return low
    return max(low, min(high, float(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _severity_score(cpu_usage: float, memory_usage: float, response_time: float, anomaly_score: float) -> float:
    cpu_norm = _bounded(cpu_usage / 100.0)
    memory_norm = _bounded(memory_usage / 100.0)
    latency_norm = _bounded(response_time / 3000.0)
    anomaly_norm = _bounded((abs(anomaly_score) + 0.2) / 1.4)
    return _bounded(0.35 * cpu_norm + 0.25 * memory_norm + 0.25 * latency_norm + 0.15 * anomaly_norm)


def _finalize_plan(
    plan: ResolutionPlan,
    anomaly_label: int,
    failure_probability: float,
    root_cause: str,
) -> Dict[str, Any]:
    """Enforce alerting policy when auto-remedy isn't available."""
    is_incident = anomaly_label == 1 or failure_probability >= 0.5

    if not is_incident:
        return asdict(plan)

    known_cause = root_cause in {"CPU_OVERLOAD", "MEMORY_LEAK", "LATENCY_SPIKE"}
    can_auto_resolve = bool(plan.can_auto_execute and known_cause and plan.resolution_confidence >= 0.60)

    if can_auto_resolve:
        return asdict(ResolutionPlan(
            auto_resolution=plan.auto_resolution,
            resolution_playbook=plan.resolution_playbook,
            resolution_confidence=plan.resolution_confidence,
            can_auto_execute=True,
            resolution_status="AUTO_REMEDIATION_EXECUTED",
            resolution_alert="",
        ))

    return asdict(ResolutionPlan(
        auto_resolution=plan.auto_resolution,
        resolution_playbook=plan.resolution_playbook,
        resolution_confidence=plan.resolution_confidence,
        can_auto_execute=False,
        resolution_status="MANUAL_INTERVENTION_REQUIRED",
        resolution_alert=f"⚠️ Auto-resolution unavailable for root cause '{root_cause}'. Escalate to SRE team.",
    ))


def recommend_resolution(
    root_cause: str,
    cpu_usage: float,
    memory_usage: float,
    response_time: float,
    anomaly_score: float,
    failure_probability: float,
    anomaly_label: int,
) -> Dict[str, Any]:
    """Generate automatic remediation suggestion for anomaly rows.

    If auto-remediation is not confidently possible, a dashboard-visible alert is generated.
    """
    try:
        cpu_usage = _safe_float(cpu_usage)
        memory_usage = _safe_float(memory_usage)
        response_time = _safe_float(response_time)
        anomaly_score = _safe_float(anomaly_score)
        failure_probability = _bounded(_safe_float(failure_probability))
        anomaly_label = _safe_int(anomaly_label)

        root = str(root_cause or "NORMAL").upper()

        if anomaly_label != 1 and failure_probability < 0.5:
            return asdict(ResolutionPlan(
                auto_resolution="No automated action required",
                resolution_playbook="Observe only; continue normal monitoring.",
                resolution_confidence=0.20,
                can_auto_execute=False,
                resolution_status="MONITORING",
                resolution_alert="",
            ))

        severity = _severity_score(cpu_usage, memory_usage, response_time, anomaly_score)

        if root == "CPU_OVERLOAD":
            plan = ResolutionPlan(
                auto_resolution="Auto-scale compute tier and restart hottest service",
                resolution_playbook="1) Increase replica count by +2; 2) Restart top-CPU pod/service; 3) Rebalance traffic.",
                resolution_confidence=_bounded(0.55 + 0.35 * severity + 0.10 * failure_probability),
                can_auto_execute=severity >= 0.60,
                resolution_status="PENDING",
                resolution_alert="",
            )
        elif root == "MEMORY_LEAK":
            plan = ResolutionPlan(
                auto_resolution="Roll restart memory-leaking service and cap memory",
                resolution_playbook="1) Trigger rolling restart; 2) Apply memory limit policy; 3) Enable heap diagnostics.",
                resolution_confidence=_bounded(0.58 + 0.30 * severity + 0.12 * failure_probability),
                can_auto_execute=severity >= 0.58,
                resolution_status="PENDING",
                resolution_alert="",
            )
        elif root == "LATENCY_SPIKE":
            plan = ResolutionPlan(
                auto_resolution="Shift traffic and reset high-latency upstream",
                resolution_playbook="1) Shift 20% traffic to healthy pool; 2) Flush connection pool; 3) Warm cache layer.",
                resolution_confidence=_bounded(0.50 + 0.32 * severity + 0.10 * failure_probability),
                can_auto_execute=severity >= 0.62,
                resolution_status="PENDING",
                resolution_alert="",
            )
        else:
            plan = ResolutionPlan(
                auto_resolution="Run safe remediation workflow",
                resolution_playbook="1) Capture diagnostics; 2) Restart impacted component; 3) Escalate if no recovery in 5 min.",
                resolution_confidence=_bounded(0.45 + 0.25 * severity + 0.08 * failure_probability),
                can_auto_execute=False,
                resolution_status="PENDING",
                resolution_alert="",
            )

        return _finalize_plan(plan, anomaly_label=anomaly_label, failure_probability=failure_probability, root_cause=root)

    except Exception:
        # Unknown internal error fallback: always return stable output schema.
        return asdict(ResolutionPlan(
            auto_resolution="Fallback remediation: capture diagnostics and escalate",
            resolution_playbook="1) Save metrics snapshot; 2) Restart impacted service safely; 3) Escalate to on-call.",
            resolution_confidence=0.10,
            can_auto_execute=False,
            resolution_status="MANUAL_INTERVENTION_REQUIRED",
            resolution_alert="⚠️ Unknown model error. Escalate to SRE team with diagnostics.",
        ))
