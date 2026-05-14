from osidb_mcp.query_filters import FLAWS_EXTRA_KEYS, merge_extra_query
from osidb_mcp.tools_read import get_cve_summary


def test_merge_extra_allowlisted():
    base = {"limit": 10, "offset": 0}
    out = merge_extra_query(
        base,
        {"title": "x"},
        allowlist=FLAWS_EXTRA_KEYS,
    )
    assert out["title"] == "x"
    assert out["limit"] == 10


def test_merge_extra_rejects_unknown():
    base = {"limit": 1}
    try:
        merge_extra_query(
            base,
            {"not_a_real_osidb_key": 1},
            allowlist=FLAWS_EXTRA_KEYS,
        )
    except ValueError as e:
        assert "not allowed" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_get_cve_summary_invalid_group_by():
    r = get_cve_summary(group_by="nope")
    assert r["ok"] is False
    assert "group_by" in r.get("detail", "")
