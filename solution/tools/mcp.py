"""MCP connectors: remote MCP servers whose tools the agent gets automatically.

Nothing here is imported in agent.py. The build finds `mcp` in tools/mcp.py, builds
the MCP clients, and adds each server's tools as `<server>_<tool>`, e.g.
`github_create_pull_request`.
"""

from managed_deepagents import connections, define_mcp

from github_headers import GITHUB_HEADERS

mcp = define_mcp(
    servers={
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            # Your fine-grained GitHub token, stored in LangSmith as the
            # `patch-github` connection. Under `mda dev` it's read from
            # MDA_DEV_PATCH_GITHUB in .env instead. Never in code.
            "connection": connections.get("patch-github", {"type": "agent"}),
            "headers": GITHUB_HEADERS,  # see github_headers.py
            # Only the tools Patch needs, by their raw MCP names.
            "include_tools": [
                "create_branch",
                "push_files",
                "create_pull_request",
                "list_pull_requests",  # used by schedules/pr_roundup.py
            ],
        },
    },
    # If GitHub's server can't load (e.g. no credentials yet), start without it
    # instead of failing the run.
    throw_on_load_error=False,
)
