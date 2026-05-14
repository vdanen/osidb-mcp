# Changelog

## 0.1.3

- Add `search_component`, `query_affects`, `get_pending_exploit_actions`; `search_flaws` adds major-incident filters.
- README: full MCP tools table and “when to use which” guidance; TOOLS.md reference for tool details and example prompts.

## 0.1.2

- Add `osidb-mcp --version` / `-V` (no credentials or `OSIDB_BASE_URL` required).

## 0.1.1

- Add high-level MCP tools aligned with common CVE servers: `search_flaws`, `get_flaw_details`, `get_cve_summary`.

## 0.1.0

- Initial release: stdio MCP server, `readonly` / `readwrite` access mode (read tools only; mutations reserved for a later release), OSIDB session via `osidb-bindings` (Kerberos or basic auth).
