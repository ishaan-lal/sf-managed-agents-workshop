"""Weekday-morning roundup of open PRs, posted to a Slack channel.

The file name (`pr_roundup`) is the schedule name. Declarations are read at
compile time without running this file, so every value must be a literal.
"""

from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="3 9 * * 1-5",
    timezone="America/Los_Angeles",
    prompt=(
        "List this repository's open pull requests with github_list_pull_requests. "
        "Reply with one line per PR: title, link, and days open. Flag any open "
        "more than 3 days. If there are none, say so in one line. Do not change "
        "any code."
    ),
    deliver_to={
        "channel": "slack",
        # The Slack channel to post in: channel name > About > Channel ID.
        # Invite your bot there (`/invite @Patch-<you>`).
        "to": {"type": "provider_conversation", "conversation_id": "C0000000000"},
    },
)
