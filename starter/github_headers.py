"""Workaround for GitHub's MCP server. Provided for you: no need to change it.

GitHub's hosted MCP server requires each tool call's `owner` and `repo`
arguments to also be sent as `Mcp-Param-owner` / `Mcp-Param-repo` HTTP headers
(MCP spec SEP-2243), and the runtime's MCP client doesn't send them yet.
Without them every GitHub tool fails with
`header mismatch: missing Mcp-Param-owner header`.

Patch only ever works on your fork, so the values never change: they come from
PATCH_REPO via config.py. Remove this once the MCP client sends them itself.
"""

from config import REPO

_OWNER, _, _NAME = REPO.partition("/")

GITHUB_HEADERS = {"Mcp-Param-owner": _OWNER, "Mcp-Param-repo": _NAME}
