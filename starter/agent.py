"""My Patch: fixes bugs and builds small features in my fork of the game.

This is the only required file in a managed agent project. Most features turn
on when a file sits in the right place (sandbox/, tools/mcp.py, channels/, ...),
not by changing this one. Middleware is the exception: it's plain code, so
it's imported and wired in here.
"""

from managed_deepagents import define_deep_agent

from middleware.checkout import ensure_checkout

agent = define_deep_agent(
    # TODO(step 1): name your agent: letters, numbers, underscores, or hyphens,
    # starting with a letter, e.g. "patch-ada". It becomes your deployment's
    # name in LangSmith, so make it unique in the workshop workspace.
    name="TODO",
    model="anthropic:claude-sonnet-5-5",
    # Clones your fork into the sandbox before every turn. Does nothing until
    # the sandbox exists (step 2).
    middleware=[ensure_checkout],
    # TODO(step 3): pause before a pull request opens, with interrupt_on.
)
