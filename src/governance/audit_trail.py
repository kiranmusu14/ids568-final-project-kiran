"""
Hash-chained audit trail for the IDS 568 RAG governance packet.

Each event is serialized to a canonical JSON string (sort_keys=True) and
hashed with SHA-256.  The hash of event N is included in the payload of
event N+1 as previous_hash, forming a chain.  Any post-hoc modification of
an earlier event invalidates all subsequent hashes, making tampering
detectable without a trusted third-party timestamp service.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common.config import ROOT, settings


@dataclass
class AuditEvent:
    event_id: str
    event_type: str
    timestamp: str
    actor: str
    resource_id: str
    action: str
    details: dict[str, Any]
    previous_hash: str
    event_hash: str


def _hash(payload: str) -> str:
    return hashlib.new(settings.audit_hash_algorithm, payload.encode("utf-8")).hexdigest()


def build_audit_log() -> list[AuditEvent]:
    raw_events = [
        ("evt-001", "MODEL_DEPLOYED", "mlops_architect", "rag-service", "deploy baseline", {"version": "1.0.0"}),
        ("evt-002", "PROMPT_TEMPLATE_CHANGED", "mlops_architect", "prompt-template", "promote prompt", {"template_version": "rag-v3"}),
        ("evt-003", "KNOWLEDGE_BASE_UPDATED", "data_engineer", "kb-index", "refresh controls corpus", {"documents_added": 14}),
        ("evt-004", "APPROVAL_GRANTED", "governance_lead", "release-ticket", "approve guarded rollout", {"ticket": "CAB-568"}),
        (
            "evt-005",
            "MONITORING_ALERT",
            "oncall_engineer",
            "grafana-alert",
            "empty retrieval alert fired",
            {"empty_retrieval_rate": settings.drift_current_empty_retrieval_rate},
        ),
        ("evt-006", "INTERVENTION", "oncall_engineer", "retriever-config", "raise retrieval top-k", {"top_k": 4}),
    ]
    events: list[AuditEvent] = []
    previous_hash = "GENESIS"
    base_timestamp = datetime.fromisoformat(settings.audit_base_timestamp)
    if base_timestamp.tzinfo is None:
        base_timestamp = base_timestamp.replace(tzinfo=timezone.utc)
    for index, (event_id, event_type, actor, resource_id, action, details) in enumerate(raw_events):
        timestamp = (base_timestamp + timedelta(seconds=index * settings.audit_event_spacing_seconds)).isoformat()
        payload = json.dumps(
            {
                "event_id": event_id,
                "event_type": event_type,
                "timestamp": timestamp,
                "actor": actor,
                "resource_id": resource_id,
                "action": action,
                "details": details,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
        )
        event_hash = _hash(payload)
        events.append(
            AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=timestamp,
                actor=actor,
                resource_id=resource_id,
                action=action,
                details=details,
                previous_hash=previous_hash,
                event_hash=event_hash,
            )
        )
        previous_hash = event_hash
    return events


AUDIT_LOG_SCHEMA_VERSION = "1.0.0"


def _events_payload(events: list[AuditEvent]) -> dict[str, Any]:
    """Serialize events as a single valid JSON document.

    The file is one JSON object so `json.load()` succeeds without any
    line-by-line parsing. Each event still carries previous_hash and
    event_hash, so the hash chain is preserved end to end.
    """
    return {
        "schema_version": AUDIT_LOG_SCHEMA_VERSION,
        "hash_algorithm": settings.audit_hash_algorithm,
        "event_count": len(events),
        "events": [asdict(event) for event in events],
    }


def write_audit_log(path: Path | None = None) -> Path:
    output = path or ROOT / "logs" / settings.audit_trail_filename
    output.parent.mkdir(parents=True, exist_ok=True)
    events = build_audit_log()
    output.write_text(json.dumps(_events_payload(events), indent=2) + "\n")
    return output


def _load_events(source: Path) -> list[dict[str, Any]]:
    """Read events from either the canonical JSON document or legacy JSONL."""
    raw = source.read_text().strip()
    if not raw:
        return []
    if raw.startswith("{"):
        document = json.loads(raw)
        return list(document.get("events", []))
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def verify_audit_log(path: Path | None = None) -> bool:
    source = path or ROOT / "logs" / settings.audit_trail_filename
    previous_hash = "GENESIS"
    for payload in _load_events(source):
        expected = _hash(
            json.dumps(
                {
                    "event_id": payload["event_id"],
                    "event_type": payload["event_type"],
                    "timestamp": payload["timestamp"],
                    "actor": payload["actor"],
                    "resource_id": payload["resource_id"],
                    "action": payload["action"],
                    "details": payload["details"],
                    "previous_hash": previous_hash,
                },
                sort_keys=True,
            )
        )
        if expected != payload["event_hash"]:
            return False
        previous_hash = payload["event_hash"]
    return True


if __name__ == "__main__":
    path = write_audit_log()
    print(f"Audit trail written to {path}")
    print(f"Integrity valid: {verify_audit_log(path)}")
