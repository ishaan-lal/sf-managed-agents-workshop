"""Patch: fixes bugs and builds small features in a web game, then opens a PR.

The sandbox, Slack channel, memory, schedule, skills, and MCP servers are all
declared by where their files sit in the project. Only middleware, which is
plain code, is imported here.
"""

from managed_deepagents import define_deep_agent

from middleware.checkout import ensure_checkout

agent = define_deep_agent(
    # Also your deployment's name. In a shared LangSmith workspace, make it
    # unique, e.g. "patch-ishaan".
    name="patch",
    model="anthropic:claude-sonnet-5-5",
    middleware=[ensure_checkout],
    # Pause before a pull request opens. MCP tools are named <server>_<tool>.
    # Slack's approval buttons support approve and reject only.
    interrupt_on={
        "github_create_pull_request": {"allowed_decisions": ["approve", "reject"]},
    },
)
