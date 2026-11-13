"""MCP servers: remote tool providers whose tools Patch gets automatically.

Nothing here is imported in agent.py. The build finds `mcp` in tools/mcp.py,
builds the MCP clients, and adds each server's tools as `<server>_<tool>`,
e.g. `github_create_pull_request`.
"""

from managed_deepagents import define_mcp

from github_headers import GITHUB_HEADERS

mcp = define_mcp(
    servers={
        # GitHub's own MCP server: branches, commits, pull requests.
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            # TODO(step 3): add the `connection` that holds your GitHub token.
            # Provided workaround, leave it in: see github_headers.py.
            "headers": GITHUB_HEADERS,
            # TODO(step 1): GitHub's server has ~46 tools. List ONLY the four
            # Patch needs, by their raw names (the README has the table).
            "include_tools": ["TODO"],
        },
        # Web search that LangSmith runs for you. No API key, no connection.
        "web": {
            "transport": "http",
            "url": "https://api.smith.langchain.com/v1/managed-tools/servers/parallel/mcp",
        },
    },
    # If one server is down, start with the others instead of failing the run.
    throw_on_load_error=False,
)
