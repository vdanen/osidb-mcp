"""FastMCP application wiring (stdio)."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from osidb_mcp.config import AccessMode, Settings
from osidb_mcp import tools_read

logger = logging.getLogger(__name__)

_INSTRUCTIONS = """\
This server exposes read-only OSIDB operations (flaws/CVEs, affects, trackers, comments, references, CVSS) \
via official osidb-bindings. Responses may include embargoed data depending on your OSIDB account.

Use high-level tools ``search_flaws``, ``get_flaw_details``, and ``get_cve_summary`` for triage-style search and rollups; \
use lower-level ``flaws_list`` / ``flaws_count`` when you need full filter control.

Access mode is controlled only by the ``OSIDB_MCP_ACCESS_MODE`` environment variable (``readonly`` default; \
``readwrite`` reserved for future mutation tools).
"""


def create_server(settings: Settings) -> FastMCP:
    mcp = FastMCP("osidb-mcp", instructions=_INSTRUCTIONS)

    mcp.tool(name="osidb_status", description="OSIDB API health / status payload.")(
        tools_read.osidb_status
    )
    mcp.tool(
        name="osidb_whoami",
        description="Current authenticated OSIDB user / profile (from /osidb/whoami).",
    )(tools_read.osidb_whoami)
    mcp.tool(
        name="flaw_get",
        description="Retrieve a single flaw by CVE id or flaw id; optional field projection.",
    )(tools_read.flaw_get)
    mcp.tool(
        name="search_flaws",
        description=(
            "Search CVEs/flaws by keyword, CVE id(s), severity (impact), changed date range, "
            "PS product modules or components, workflow, major incident state, embargo, and owner. "
            "Keyword-only queries use OSIDB full-text search; structured filters use list APIs."
        ),
    )(tools_read.search_flaws)
    mcp.tool(
        name="get_flaw_details",
        description=(
            "Full flaw/CVE payload plus affected products (affects) and trackers "
            "(Jira/Bugzilla filings) for one flaw or CVE id."
        ),
    )(tools_read.get_flaw_details)
    mcp.tool(
        name="get_cve_summary",
        description=(
            "Executive-style aggregates: flaw counts by severity (impact) and by workflow state, "
            "with optional scope filters (dates, modules, components, embargo, owner). "
            "Runs multiple OSIDB count queries (see group_by: severity | workflow | both)."
        ),
    )(tools_read.get_cve_summary)
    mcp.tool(
        name="flaws_list",
        description=(
            "List flaws with filters: components, affects (ps_module/ps_component/ps_update_stream), "
            "workflow_state, impact, owner_isempty, embargoed, dates, etc. "
            "Optional ``extra_query`` must use OSIDB v2 list query keys (allowlisted). "
            "limit is capped at 100."
        ),
    )(tools_read.flaws_list)
    mcp.tool(
        name="flaws_count",
        description="Count flaws matching the same filters as flaws_list (no result bodies).",
    )(tools_read.flaws_count)
    mcp.tool(
        name="flaws_search",
        description="Full-text search flaws (maps to OSIDB search parameter).",
    )(tools_read.flaws_search)
    mcp.tool(
        name="affects_list",
        description=(
            "List affects with ps_module / ps_component / ps_update_stream and flaw__ filters "
            "(e.g. flaw_workflow_state_in, flaw_impact_in, flaw_components_in)."
        ),
    )(tools_read.affects_list)
    mcp.tool(
        name="trackers_list",
        description="List trackers (filings) with optional CVE / ps_module / ps_component filters.",
    )(tools_read.trackers_list)
    mcp.tool(
        name="flaw_comments_list",
        description="Paginated comments for a flaw id.",
    )(tools_read.flaw_comments_list)
    mcp.tool(
        name="flaw_references_list",
        description="Paginated external references for a flaw id.",
    )(tools_read.flaw_references_list)
    mcp.tool(
        name="flaw_cvss_scores_list",
        description="Paginated CVSS score rows for a flaw id.",
    )(tools_read.flaw_cvss_scores_list)
    mcp.tool(
        name="search_component",
        description=(
            "Find flaws touching flaw-level ``components`` values (``components_in``). "
            "For PS ``ps_component`` filters, use ``search_flaws`` / ``flaws_list`` instead."
        ),
    )(tools_read.search_component)
    mcp.tool(
        name="query_affects",
        description="List affect rows for one or more CVE ids (v2 affects API); thin wrapper over ``affects_list``.",
    )(tools_read.query_affects)
    mcp.tool(
        name="get_pending_exploit_actions",
        description=(
            "[EXPERIMENTAL] Pending exploit / IR actions from ``GET /exploits/api/v1|v2/report/pending``. "
            "May fail if the exploits integration is not enabled on this OSIDB instance."
        ),
    )(tools_read.get_pending_exploit_actions)

    if settings.access_mode == AccessMode.readwrite:
        logger.warning(
            "readwrite mode requested: mutation tools are not implemented in this release; "
            "only read tools are registered."
        )

    return mcp
