"""Slack: DM Patch or @mention it in a channel. Set up by `mda deploy`.

No Slack app to create and no tokens in .env. On deploy, the CLI prints a link
to create and install the app; after that the bot DMs you. Files dropped in
the thread land in the sandbox under /workspace/attachments/, and the agent
sends files back with `upload_files`.
"""

from managed_deepagents import channels

channel = channels.slack(
    # Everyone's bot lives in the same workshop Slack, so make yours easy to
    # tell apart, e.g. "Patch-Ishaan".
    name="Patch",
    description="Fixes bugs and builds small features in the Tetris game, then opens a PR.",
    background_color="#1C3C3C",
)
