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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
        ("evt-005", "MONITORING_ALERT", "oncall_engineer", "grafana-alert", "empty retrieval alert fired", {"empty_retrieval_rate": 0.17}),
        ("evt-006", "INTERVENTION", "oncall_engineer", "retriever-config", "raise retrieval top-k", {"top_k": 4}),
    ]
    events: list[AuditEvent] = []
    previous_hash = "GENESIS"
    for event_id, event_type, actor, resource_id, action, details in raw_events:
        timestamp = datetime.now(timezone.utc).isoformat()
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


def write_audit_log(path: Path | None = None) -> Path:
    output = path or ROOT / "logs" / "audit_trail.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    events = build_audit_log()
    output.write_text("\n".join(json.dumps(asdict(event)) for event in events) + "\n")
    return output


def verify_audit_log(path: Path | None = None) -> bool:
    source = path or ROOT / "logs" / "audit_trail.jsonl"
    previous_hash = "GENESIS"
    for line in source.read_text().splitlines():
        payload = json.loads(line)
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
