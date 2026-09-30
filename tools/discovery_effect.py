from __future__ import annotations

import hashlib
import json
from typing import Any


DISCOVERY_EFFECT_SCHEMA_VERSION = "DISCOVERY_EFFECT_ATTEMPT_V0"
WIP_SOURCE_REF = "main@12a7c23dbe0482fd7bfe63659e54526778efef1e"

_STATE_TO_PHASE = {
    "PREPARED": "PRE_EFFECT",
    "ATTEMPTED": "POST_EFFECT_UNVERIFIED",
    "VERIFIED": "POST_EFFECT_VERIFIED",
    "FAILED": "TERMINAL_FAILURE",
    "AMBIGUOUS": "OUTCOME_UNKNOWN",
    "RECONCILED": "RECONCILED",
}


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _retry_disposition(event: dict[str, Any]) -> str:
    state = event["state"]
    if state in {"VERIFIED", "RECONCILED"}:
        return "DO_NOT_RETRY"
    if state == "FAILED":
        return "DOMAIN_DECIDES"
    if state in {"ATTEMPTED", "AMBIGUOUS"}:
        return "INSPECT_BEFORE_RETRY"
    instruction = event["recovery_instruction"]
    if instruction == "inspect_before_retry":
        return "INSPECT_BEFORE_RETRY"
    if instruction == "no_retry_required":
        return "DO_NOT_RETRY"
    raise ValueError("unsupported WIP recovery instruction")


def operation_event_envelope(event: dict[str, Any]) -> dict[str, Any]:
    """Translate one validated WIP operation event into the neutral envelope.

    The result is observational interchange only. It does not authorize retry,
    reconciliation, completion, or any external effect.
    """
    if type(event) is not dict:
        raise ValueError("operation event must be an object")
    if event.get("schema_version") != "1.0":
        raise ValueError("unsupported WIP operation-event schema")
    state = event.get("state")
    if state not in _STATE_TO_PHASE:
        raise ValueError("unsupported WIP operation state")
    for key in ("workspace_id", "operation_id", "action_class", "recovery_instruction"):
        if type(event.get(key)) is not str or not event[key]:
            raise ValueError(f"WIP event {key} is required")
    sequence = event.get("sequence")
    if type(sequence) is not int or sequence < 1:
        raise ValueError("WIP event sequence must be a positive integer")

    target = event.get("target")
    if type(target) is not dict:
        raise ValueError("WIP event target must be an object")
    if type(target.get("kind")) is not str or not target["kind"]:
        raise ValueError("WIP event target.kind is required")
    if type(target.get("locator")) is not str or not target["locator"]:
        raise ValueError("WIP event target.locator is required")
    expected = target.get("expected_precondition")
    if expected is not None and type(expected) is not str:
        raise ValueError("WIP expected_precondition must be string or null")

    if state in {"VERIFIED", "RECONCILED"}:
        receipt = event.get("effect_receipt")
        if type(receipt) is not dict:
            raise ValueError(f"WIP {state} event requires effect_receipt")
        if type(receipt.get("kind")) is not str or not receipt["kind"]:
            raise ValueError("WIP effect receipt kind is required")
        if type(receipt.get("value")) is not str or not receipt["value"]:
            raise ValueError("WIP effect receipt value is required")

    receipts = [
        {"kind": "workspace_id", "value": event["workspace_id"]},
        {"kind": "sequence", "value": str(sequence)},
        {"kind": "recovery_instruction", "value": event["recovery_instruction"]},
    ]
    previous = event.get("previous_event")
    if previous is not None:
        if type(previous) is not str or not previous:
            raise ValueError("WIP previous_event must be non-empty string or null")
        receipts.append({"kind": "previous_event", "value": previous})

    effect_receipt = event.get("effect_receipt")
    if isinstance(effect_receipt, dict):
        receipts.append(
            {
                "kind": f"effect_receipt:{effect_receipt['kind']}",
                "value": effect_receipt["value"],
            }
        )
        readback = effect_receipt.get("readback")
        if isinstance(readback, str) and readback:
            receipts.append({"kind": "effect_readback", "value": readback})

    result_summary = event.get("result_summary")
    if isinstance(result_summary, str) and result_summary:
        receipts.append({"kind": "result_summary", "value": result_summary})

    return {
        "schema_version": DISCOVERY_EFFECT_SCHEMA_VERSION,
        "source_system": "wip",
        "source_operation_id": event["operation_id"],
        "source_state": state,
        "source_ref": WIP_SOURCE_REF,
        "source_payload_sha256": _canonical_sha256(event),
        "action_class": event["action_class"],
        "target": {
            "kind": target["kind"],
            "locator": target["locator"],
            "expected_precondition": expected,
        },
        "normalized_phase": _STATE_TO_PHASE[state],
        "retry_disposition": _retry_disposition(event),
        "receipts": receipts,
    }


__all__ = [
    "DISCOVERY_EFFECT_SCHEMA_VERSION",
    "WIP_SOURCE_REF",
    "operation_event_envelope",
]
