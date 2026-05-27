"""Append-only audit log — NIST 800-53 AU-2/AU-3 / DISA STIG V-222496.

Records security-relevant events with a hash chain so tampering with prior
entries breaks subsequent hashes. Never stores raw PII; only the hashed
IP + a short event_type code + a JSON payload of non-PII fields.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Session, select


class SecurityEvent(SQLModel, table=True):
    __tablename__ = "security_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    event_type: str = Field(index=True)  # e.g. "review_submitted", "scam_report"
    actor_ip_hash: Optional[str] = Field(default=None, index=True)
    target_id: Optional[str] = Field(default=None, index=True)  # e.g. review id
    payload_json: str = "{}"
    prev_hash: Optional[str] = None
    self_hash: str = ""


def _compute_hash(prev: Optional[str], created_at: datetime, event_type: str,
                  actor_ip_hash: Optional[str], target_id: Optional[str],
                  payload_json: str) -> str:
    h = hashlib.sha256()
    h.update((prev or "").encode())
    h.update(created_at.isoformat().encode())
    h.update(event_type.encode())
    h.update((actor_ip_hash or "").encode())
    h.update((target_id or "").encode())
    h.update(payload_json.encode())
    return h.hexdigest()


def log_event(
    session: Session,
    *,
    event_type: str,
    actor_ip_hash: Optional[str] = None,
    target_id: Optional[str] = None,
    payload: Optional[dict] = None,
) -> SecurityEvent:
    payload_json = json.dumps(payload or {}, separators=(",", ":"), sort_keys=True)
    prev = session.exec(
        select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(1)
    ).first()
    prev_hash = prev.self_hash if prev else None
    now = datetime.utcnow()
    self_hash = _compute_hash(prev_hash, now, event_type, actor_ip_hash, target_id, payload_json)
    event = SecurityEvent(
        created_at=now,
        event_type=event_type,
        actor_ip_hash=actor_ip_hash,
        target_id=target_id,
        payload_json=payload_json,
        prev_hash=prev_hash,
        self_hash=self_hash,
    )
    session.add(event)
    session.flush()
    return event
