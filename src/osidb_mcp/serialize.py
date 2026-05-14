"""JSON-friendly serialization for bindings models and responses."""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any
from uuid import UUID


def to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(x) for x in obj]
    if hasattr(obj, "to_dict"):
        return to_jsonable(obj.to_dict())
    return str(obj)


def paginated_summary(
    response: Any,
    *,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    """Common pagination envelope for list endpoints."""
    results = getattr(response, "results", ()) or ()
    out: dict[str, Any] = {
        "count": getattr(response, "count", None),
        "limit": limit,
        "offset": offset,
        "results": [to_jsonable(r) for r in results],
    }
    next_url = getattr(response, "next_", None)
    if next_url:
        out["next"] = next_url
        out["next_offset"] = offset + len(results)
    return out
