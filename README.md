# Build Patch: a coding agent that lives in Slack

In this workshop you build **Patch**, a [managed agent](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview)
that fixes bugs in a small browser game and opens pull requests. You'll
report a bug in Slack (or drop in a screenshot of it), and Patch will clone the
code into its own sandbox, find the cause, fix it, verify the fix, ask you to
approve, and open a PR on GitHub.

Most of Patch is provided in `starter/`, with a few blanks for you to fill in.
Then you spend the workshop on what makes a managed agent different: a sandbox,
connections, Slack, and schedules.

| Step | You build | Managed agent feature |
|---|---|---|
| 1 | Fill-ins in the provided files | The agent, its instructions, skills, and MCP tools |
| 2 | `sandbox/` | Its own computer, one per conversation |
| 3 | A connection, `interrupt_on`, a deploy | Credentials kept out of code, human approval, hosting |
| 4 | `channels/slack.py` | Patch in Slack |
| 5 | `schedules/` | A PR roundup it posts on its own |
| 6 *(optional)* | `memory.py` | Memory across conversations: shared and per-person |

## What's in this repo

```
starter/      <- your agent. Most of Patch is provided, with TODO(step N) blanks for you to fill in.
solution/     <- the finished Patch (the answer key). Try each step first, then compare.
```

---

## 0. Before you start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), a
GitHub account, a [LangSmith](https://smith.langchain.com) API key for a
workspace with Managed Agents access, and an Anthropic API key.

1. The code for the game exists here: [ishaan-lal/simple-game](https://github.com/ishaan-lal/simple-game). **Create a fork of the repo**, and keep it **public**.
2. **Make a GitHub token for your fork only.** Open
   [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
   (GitHub → *Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token*) and fill it in:

   | Field | Set it to |
   |---|---|
   | *Token name* | `patch-workshop` |
   | *Expiration* | 30 days (anything past the workshop) |
   | *Resource owner* | Your own account |
   | *Repository access* | **Only select repositories** → pick your fork |
   | *Repository permissions* → **Contents** | **Read and write** |
   | *Repository permissions* → **Pull requests** | **Read and write** |

   Leave everything else alone. *Metadata: Read-only* turns on by itself.
   Click **Generate token** and copy it now, because GitHub shows it only once.

   > **Check both permissions before you generate.** New tokens start out
   > read-only. A read-only token still lets Patch clone and read your fork,
   > so nothing looks wrong until it tries to open a PR and gets
   > `403 Resource not accessible by personal access token`. If that happens,
   > edit the token on GitHub and fix the permissions. The token value
   > doesn't change, so you don't need to update `.env` or the connection.

   The token is Patch's guardrail: whatever anyone says to it, it can only
   touch your fork.
3. **Join the workshop Slack** (link from your facilitator).
4. **Fill in `.env`:**
   ```bash
   cd starter
   uv sync
   cp .env.example .env
   ```
   Fill in `LANGSMITH_API_KEY`, `ANTHROPIC_API_KEY`, and `MDA_DEV_PATCH_GITHUB`
   (the token). You'll fill in `PATCH_REPO` in step 1.


### The bug board

Your fork has real bugs planted in it. You'll point Patch at them as you go:

| # | What players report |
|---|---|
| 🐛 1 | The pause screen says to press Space to resume, but Space doesn't unpause it. |
| 🐛 2 | The level goes up way too fast. I'm on level 3 after only 10 lines. |
| 🐛 3 | Z is supposed to rotate counter-clockwise, but it spins pieces the same way as X. |
| 🤔 4 | I think hard drops give the wrong score. *(Do they? Patch should check before "fixing" anything.)* |

---

## Step 1: Set up the base

**Goal:** Patch knows its job, has its procedures, and has its tools declared.
Most of that is already written in `starter/`. You fill in a few blanks.

Open `starter/` and look around. These files are provided:

| File | What it is |
|---|---|
| `agent.py` | The agent definition: its name, model, and middleware. The only required file |
| `config.py` | The one place that names your fork |
| `middleware/checkout.py` | Clones your fork into the sandbox before every turn (it does nothing until step 2) |
| `instructions.md` | Patch's system prompt: its job, how to work, how to reply |
| `skills/` | Procedures Patch loads only when a task needs them |
| `tools/mcp.py` | The MCP servers Patch gets tools from: GitHub and web search |
| `github_headers.py` | A workaround for GitHub's MCP server. Leave it alone |

Each blank is marked `TODO(step 1)`. There are five.

### `agent.py`

Every agent needs a name. It's also your deployment's name in the shared
LangSmith workspace, so it has to be different from everyone else's.

**How to set it up:** set `name` to something unique: letters, numbers, `_` or
`-`, starting with a letter, like `patch-ada`.

### `config.py`

`config.py` holds two constants that other files import: `REPO` (your fork,
which the checkout middleware clones) and `CHECKOUT` (where it's cloned to).
Your fork's name differs per person, so it lives in `.env`, not in code.

**How to set it up:**

1. Open `starter/.env` and set:
   ```bash
   PATCH_REPO=<your-github-username>/simple-game
   ```
2. In `config.py`, `REPO` reads it with `os.environ.get("TODO", "")`. Replace
   `"TODO"` with the key you just set.

### `instructions.md`

This is Patch's system prompt, and it's where Patch's judgment comes from.
Most of it is written: its job, its workspace, how to classify a request, how
to use its tools, and how to reply. Read it.

**How to set it up:** fill in the two sections marked `TODO(step 1)`. Replace
each `<!-- ... -->` comment with your own text, written to Patch ("Run...",
"Never..."):

- **Verifying your change.** The game has no test suite, so how should Patch
  check its work before saying it's done? The comment has guiding questions.
- **Rules.** Two or three rules about scope: what Patch should never do while
  fixing something.

### `skills/add-a-feature/SKILL.md`

A **skill** is a procedure written in Markdown. At startup Patch sees only each
skill's `name` and `description`, and it reads the full file only when a task
matches. Two skills are written (`fix-a-bug`, `open-a-pull-request`). Read
`fix-a-bug`, then open `skills/add-a-feature/SKILL.md` and fill in that skill!

**How to set it up:**

- `description`: the **only** thing Patch reads when deciding whether to load
  the skill, so say exactly when it applies. Copy the shape of `fix-a-bug`'s.
- The steps: 4–6 numbered steps. The comment lists what a good procedure covers.

### `tools/mcp.py`

**MCP servers** are remote tool providers. `tools/mcp.py` declares two:
GitHub's server (branches, commits, PRs) and web search. GitHub's server has
about 46 tools. Fewer tools means fewer ways to go wrong, so Patch gets only
the four it needs.

**How to set it up:** set `include_tools` to these four names:

| Tool | What Patch uses it for |
|---|---|
| `create_branch` | Make a branch for the change |
| `push_files` | Push every changed file in one commit |
| `create_pull_request` | Open the PR |
| `list_pull_requests` | List open PRs (the schedule in step 5 uses it) |

Patch sees each one as `<server>_<tool>`, e.g. `github_create_branch`. The
GitHub server has no credentials yet. You'll add them in step 3.

### Run it

```bash
uv run mda dev
```

Studio opens in your browser. **In the graph dropdown at the top, pick the one
named after your agent** (e.g. `patch-ada`). You might see
`patch-ada--general-purpose`, which you **should not** select.

### Checkpoint

Patch has no computer yet, so it can't touch the game. But it already knows
everything you set up. Ask each question in a **new thread** and check the
answer against your files.

**Your instructions:**

> What's your job, and how do you decide whether a message is a bug report or a feature request?

It describes its job and the bug-versus-feature rule from `instructions.md`.

> Before you tell me a change is done, how do you check it?

It describes the checks **you** wrote in *Verifying your change*. If the answer
is vague, so is your section.

**Your skills:**

> What skills do you have, and when would you use each one?

It lists `fix-a-bug`, `add-a-feature` and `open-a-pull-request`, and describes
each from its `description`. If it can't say when to use `add-a-feature`, your
description is too vague.

> Walk me through how you'd add a key that toggles the ghost piece.

In the trace, it reads `/skills/add-a-feature/SKILL.md` and follows **your**
steps.

**Its limits:**

> What's in /workspace/app?

It can't tell you: it has no machine to run commands on, and nothing has been
cloned. That's step 2.

You won't see any `github_*` tools yet. The GitHub server has no credentials
until step 3, so it's skipped for now. `config.py` gets used in step 2, when
the checkout middleware clones your fork.

---

## Step 2: Give it a computer (sandbox)

**Goal:** To fix bugs and implement features, Patch needs the ability to write and run code. We provide this with a sandbox!

### `sandbox/__init__.py`

This file declares the sandbox, and having a `sandbox/` folder is what turns
it on. With it, every conversation (thread) gets its own isolated machine, so
Patch can run real commands, and two people's work never collides. Sandboxes
cost resources while they're up, so you also tell it when to clean up.

**How to set it up:** create a `sandbox/` folder at the root of `starter/`,
and in it an `__init__.py` that exports a variable named `sandbox`:

```python
from managed_deepagents import define_sandbox

sandbox = define_sandbox(idle_ttl_seconds=..., default_timeout=...)
```

- `idle_ttl_seconds`: delete a sandbox after **30 minutes** without activity.
- `default_timeout`: stop any single shell command after **5 minutes**, so a
  hung command can't stall Patch forever.

### `sandbox/setup.sh`

A fresh sandbox is a bare machine. Patch needs `git` to clone the game and
read its diffs, and `node` to check its JavaScript with `node --check`. The
game has no test suite, so `node --check` is how Patch catches syntax errors.
`setup.sh` installs that tooling.

It runs **once**, when the sandbox snapshot is built (on `uv run mda dev` or
`uv run mda deploy`), not once per conversation. Every new thread starts from
that snapshot, so tooling is already installed and threads start fast.

**How to set it up:** create `sandbox/setup.sh` with this script:

```bash
#!/usr/bin/env bash
set -euo pipefail

missing=()
command -v git  >/dev/null 2>&1 || missing+=(git)
command -v node >/dev/null 2>&1 || missing+=(nodejs)
if [ ${#missing[@]} -gt 0 ]; then
  apt-get update
  apt-get install -y --no-install-recommends "${missing[@]}"
fi

mkdir -p /workspace
```

- **`set -euo pipefail`** stops the script at the first error. A failed
  install then fails the build loudly, instead of leaving you with a broken
  snapshot.
- **The `command -v` checks** list only the tools that aren't already
  installed (the Node package is called `nodejs`).
- **`apt-get`** installs whatever is missing. The sandbox is a Debian-based
  image. If nothing is missing, this part is skipped.
- **`mkdir -p /workspace`** creates the folder the game gets cloned into.

Put tooling only in here. No repo code, because it would go stale in the
snapshot, and never any secrets.

### Middleware

Open up `middleware/checkout.py`. The middleware has been written for you. The `@before_agent` decorator indicates when the function will be fired, and the contents of the function is what occurs. In this case, the middleware function is cloning the git repo of the codebase.

In `agent.py`, see that the `middleware` parameter is set for you, so everything is already wired together.


### Checkpoint

Restart `uv run mda dev` (the first start builds the snapshot, so give it a
minute), then in a new thread:

> What's in /workspace/app? Show me the latest commit.

It's your fork. In the trace, `ensure_checkout` runs before the first model
call. Now test the instructions you wrote:

> Rename the "New game" button to "Restart". Don't open a pull request. Just make the change and tell me how you checked it.

A good run greps the **whole** repo and finds "New game" in both `index.html`
and `README.md`, reads its diff back, and says how it verified. If it only
changed the button, tighten *Verifying your change* and try again.

Then, in a **new thread**:

> What does the button next to the Next preview say?

It still says "New game". Each thread has its own sandbox, so two people never
see each other's half-finished edits.

---

## Step 3: Deploy it, and connect it to GitHub

**Goal:** We've given our agent code-writing capabilities, but it still needs the ability to push code to GitHub so as to directly improve the codebase! In this step, we'll configure a connection for the GitHub MCP. 

### Connections

Patch's GitHub tools need your GitHub token, but a token must never be written
in code, and the sandbox deliberately has no credentials. A **connection** is a
named credential stored in LangSmith. Code refers to it only by name, and the
runtime supplies the secret when a run starts. You can rotate the token
without touching code or redeploying.

A connection is either:

- **Agent-scoped** (`{"type": "agent"}`): one credential that belongs to the
  deployment. Everyone who talks to Patch uses it. 
- **User-scoped** (`{"type": "user"}`): each person connects their own
  account, usually through OAuth, and Patch acts as them. See *Going further*.

### Deploy

So far Patch has run on your laptop. Deploying runs the same project in
LangSmith: it builds the sandbox snapshot and hosts the agent. Nothing in the
code changes. Deploy now, before you touch `tools/mcp.py`. In your second
terminal, in `starter/`:

```bash
uv run mda deploy
```

The first deploy takes a few minutes. Later deploys are faster.

### Create the connection

An agent-scoped connection belongs to a deployment, which is why you deployed
first: now there's a deployment to attach it to. Store your token in LangSmith.
The first argument, `patch-github`, is the connection's **name**:

```bash
uv run mda connections create patch-github --secret-from-env MDA_DEV_PATCH_GITHUB
```

`--secret-from-env` copies the token from `MDA_DEV_PATCH_GITHUB` in `.env`, so
you never paste it on the command line.

### `tools/mcp.py`: add the connection

**How to set it up:** give the `github` server its credential. Add
`connections` to the import, and this line where the `TODO(step 3)` is:

```python
from managed_deepagents import connections, define_mcp
...
"connection": connections.get("patch-github", {"type": "agent"}),
```

- `"patch-github"` is the connection's **name**. It's how the code finds the
  credential, and it's the name you'll give the connection when you create it
  in LangSmith above. The two have to match exactly.
- `{"type": "agent"}` makes it agent-scoped: one token for the whole
  deployment.

Now, the GitHub credential (PAT) will be passed when the MCP server is called, allowing your agent to utilize the tools that the GitHub MCP exposes.

### `agent.py`: approve before a PR opens

Ideally, the agent will pause and ask us to confirm a PR before it writes it. Simply including "ask before opening a PR" in the prompt is a request that the model could skip. So we'll configure Human-in-the-Loop through `interrupt_on`: the runtime pauses the run right before the tool call and waits for a person to approve or reject it.


**How to set it up:** where the `TODO(step 3)` is, add:

```python
interrupt_on={
    "github_create_pull_request": {"allowed_decisions": ["approve", "reject"]},
},
```

- This reads as: for the `github_create_pull_request` tool, stop before running it, and ask the user for approval or rejection for the tool. 

### Redeploy

Redeploy so the agent picks up the most recent changes:

```bash
uv run mda deploy
```

The deploy checks that every connection the project declares exists in
LangSmith. `patch-github` does now, so it goes through.

### Checkpoint

In LangSmith, open **Agent Servers**, find your agent by name, and open it in
**Studio**. Pick your agent's graph, and send bug 🐛 2:

> The level goes up way too fast. I'm on level 3 after only 10 lines. Can you fix it?

It finds the cause (the README says levels rise every 10 lines; the code says
5), fixes it, creates a branch, pushes, and then **pauses** before opening the
PR. The approval card shows the title, body, and branch.

1. If you select **Reject**, no PR opens.
2. Clicking **Approve** will let the tool carry out, and a new PR will be created. **Click Approve for now**.

**You have your first PR,** opened by your deployed agent with a token that
never touched your code. Open it on GitHub.

---

## Step 4: Ship it to Slack

**Goal:** Thus far, we've only been communicating to the agent through LangSmith Studio. We can put our agent in Slack and communicate with it there through DM or @mention. For this, we need to set up a Slack channel.

### `channels/slack.py`

A **channel** makes the agent available in a different service. This file **is** the whole Slack integration: there's no
Slack app to build and no bot token in `.env`, because `uv run mda deploy`
creates and installs the app for you. Patch's instructions already have a
*Slack* section: files people attach land in `/workspace/attachments/`, and it
sends the diff back with `upload_files`.

**How to set it up:** create a `channels/` folder at the root of `starter/`,
and in it `slack.py`, which exports a variable named `channel`:

```python
from managed_deepagents import channels

channel = channels.slack(name="...", description="...")
```

- `name`: everyone's bot lives in the same Slack, so make yours easy to tell
  apart: `Patch-<your name>`. Use 1–35 characters: letters, numbers, spaces,
  `_`, `-` or `.`, and no parentheses.
- `description`: what your Patch does, up to 139 characters.
- Optionally, `background_color` for the app icon, like `"#1C3C3C"`.

### Redeploy

```bash
uv run mda deploy
```

The deploy pauses and prints a **Slack link**. Open it in a browser signed in
to the workshop Slack, install the app, and the deploy continues. When it
finishes, your bot DMs you.

### Checkpoint

In your DM with your bot:

1. **Bug 🐛 1, with a screenshot.** Open your fork's `index.html` in a browser
   (or grab the screenshot pinned in `#patch-party`), start a game, press
   **P**, and screenshot the pause screen. Upload it to your bot with:
   > The pause screen tells me to press Space to resume, but Space doesn't unpause it.

   It reads the screenshot, finds the hint in **both** `index.html` and
   `tetris.js`, fixes both, and **Approve / Reject buttons** appear in the
   thread. Approve. It replies with the PR link and attaches the diff.
2. **Follow-up, same thread:**
   > Also make the pause title all caps.

   It pushes to the **same branch**: one PR, now with two commits, and no
   second approval (the gate is on *opening* a PR).

---

## Step 5: Run it on a schedule

**Goal:** Patch posts a roundup of your fork's open PRs to Slack on a timer,
with no one messaging it.

### `schedules/pr_roundup.py`

Everything so far starts when someone sends a message. A **schedule** runs
Patch on a timer with a fixed prompt and posts the result to Slack, which
suits routine jobs like a PR roundup. The file name is the schedule's name.

**How to set it up:** create a `schedules/` folder at the root of `starter/`,
and in it `pr_roundup.py`, which exports a variable named `schedule`:

```python
from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="...",                       # 5 fields: minute hour day month weekday
    timezone="America/Los_Angeles",
    prompt="...",
    deliver_to={
        "channel": "slack",
        "to": {"type": "provider_conversation", "conversation_id": "C..."},
    },
)
```

- `cron`: run it **every 10 minutes** for the workshop, so you can watch it
  fire. (Normally you'd run it on weekday mornings.)
- `prompt`: list the repo's open PRs with `github_list_pull_requests`, one
  line per PR with title, link and days open. Flag any PR open more than 3
  days. If there are none, say so in one line. **Don't change any code.**
- `conversation_id`: the `#patch-party` channel ID from the facilitator's
  slide. Then `/invite` your bot to `#patch-party` so it can post there.
- The build reads this file at compile time **without running it**, so every
  value must be a literal: no environment variables, no function calls, no
  f-strings.

### Redeploy

```bash
uv run mda deploy
```

### Checkpoint

Within 10 minutes your bot posts your fork's open PRs to `#patch-party`,
alongside everyone else's.

---

## Step 6 (optional): Give it memory

*Do this step if you have time. Nothing later depends on it, except two
memory items in the bug bounty.*

**Goal:** Patch remembers facts about the repo for everyone, and each person's
preferences for just that person.

### `memory.py`

Every thread starts from scratch: Patch forgets what it learned about the repo
and what you told it you prefer. Memory gives it folders that last across
conversations, in two layers:

- **agent** (`/memories/agent/`) is **shared** by everyone: facts about the
  repo, so one person's discovery helps the next.
- **user** (`/memories/user/`) is **private** to each person: their
  preferences. It's on in Studio and Slack DMs and off in shared Slack
  channels, so one person's notes never leak into a group.

**How to set it up:** create `memory.py` at the root of `starter/`:

```python
from managed_deepagents import MemoryLayer, define_memory

memory = define_memory(agent=MemoryLayer(), user=MemoryLayer())
```

Each layer is a folder Patch reads and writes with its normal file tools.
Deployed, memory is stored in Context Hub.

### `instructions.md`: add a *Memory* section

We'll give a bit of guidance to the agent on when to store specific things to memory. Add the following to your `instructions.py`.

```markdown
## Memory

When someone states a lasting preference ("always...", "from now on..."), such
as opening their PRs as drafts, save it to `/memories/user/AGENTS.md`, confirm
in one line, and follow it from then on. When you learn something about this
repository that would have saved you time, add one line to
`/memories/agent/AGENTS.md`.
```

The `open-a-pull-request` skill already checks `/memories/user/AGENTS.md` for a
drafts preference, so there's nothing to add there.

### Redeploy

```bash
uv run mda deploy
```

### Checkpoint

In your DM with your bot:

1. > From now on, open my PRs as drafts.

   It saves this to `/memories/user/AGENTS.md`.
2. In a **new thread**, bug 🐛 3:
   > Z is supposed to rotate counter-clockwise, but it spins pieces the same way as X.

   The approval card says `draft: true`, which nobody asked for in this thread.

---

## Step 7: Bug bounty

You have a coding agent in Slack. Use it:

- **Skipped step 6? Fix bug 🐛 3:** `Z is supposed to rotate counter-clockwise, but it spins pieces the same way as X.`
- **Test the skill you wrote:** `Add WASD controls: A and D move left and right, S soft-drops, W rotates clockwise.`
  In the trace, it loads `add-a-feature` and follows *your* steps. Did it
  update the controls in **both** `README.md` and `index.html`?
- **Try the decoy, 🤔 4:** `I think hard drops give the wrong score. Can you check and fix it?`
  It loads `fix-a-bug`, finds the code matches the README (2 points per cell),
  and stops **without** inventing a fix.
- Ship a feature from Slack: `Add a key that toggles the ghost piece on and off. Use G.`
  · `Pause the game automatically when the window loses focus.`
  · `Show "lines until next level" under the Level stat.`
- **If you did step 6:** mention your bot in a shared channel and watch which memory layer it uses.
- **If you did step 6:** teach it something for everyone: `Remember: user-visible text lives in both index.html and tetris.js.`
  Then find it in `/memories/agent/AGENTS.md` in Context Hub.
- Merge a PR on GitHub and play the fixed game.


## Step 8: Clean up

Your schedule runs every 10 minutes, so don't skip this:

```bash
cd starter
uv run mda delete
```

It deletes the deployment, its schedules, its Slack channel connection, its
Context Hub repo (instructions, skills, memory), and its sandboxes. It asks
first. Then delete the `patch-github` connection
(`uv run mda connections delete patch-github`) and revoke your GitHub token.

---


## Troubleshooting

| Symptom | Fix |
|---|---|
| `uv run mda dev` fails building the sandbox | Read the `setup.sh` output. Check your workspace has sandbox access |
| "Set PATCH_REPO in .env" | Add your fork, as `owner/name`, to `.env`, and check `config.py` reads `PATCH_REPO` (step 1) |
| "Could not clone … into the sandbox" | Check `PATCH_REPO`'s spelling, and that your fork is public |
| No `github_*` tools in the trace | Check `include_tools` uses the raw names (`create_branch`, not `github_create_branch`). Locally, check `MDA_DEV_PATCH_GITHUB` is set in `.env`; deployed, check the `connection` line from step 3 and the `patch-github` connection |
| `403 Resource not accessible by personal access token` | The token is read-only. On GitHub, edit it: **Contents** and **Pull requests** → Read and write. Same token value, so nothing else to update |
| GitHub `401`, or logs say `MCP server "github" failed to load … rejected by its server` | The token is expired or wrong. Make a new one (*Before you start*, item 2), put it in `.env`, then delete and recreate the `patch-github` connection |
| GitHub `404` on your repo | The token doesn't include your fork (*Repository access*), or `PATCH_REPO` is misspelled |
| `header mismatch: missing Mcp-Param-owner header` | The `github` server in `tools/mcp.py` is missing its provided `"headers": GITHUB_HEADERS` line. Put it back |
| Any `mda` command: `LangSmith rejected LANGSMITH_API_KEY … (HTTP 403)` | An old key exported in your shell overrides `.env`. Run `unset LANGSMITH_API_KEY`, or fix it in your shell profile |
| Run never pauses before the PR | The `interrupt_on` key must be the full `github_create_pull_request` (one underscore) |
| A skill never loads | Its folder name must match `name:` in the frontmatter, and the `description` must say when to use it |
| Schedule fails to compile | Every value in `define_schedule` must be a literal: no env vars, function calls, or f-strings |
| Deploy stops: `connections declared by this project are not in the workspace` | Create the connection first (step 3, *Create the connection*). The name must match `tools/mcp.py` exactly |
| `connections create`: `No deployment named '…' exists in this workspace` | The connection needs a deployment to belong to. Remove the `connection` line from `tools/mcp.py`, run `uv run mda deploy`, create the connection, then put the line back and redeploy |
| `connections create` returns 403 | Your LangSmith role can't create connections. Ask the facilitator |
| Deploy waits on Slack forever | Open the printed link signed in to the *workshop* Slack. If it says an admin must approve, ask the facilitator |
| Bot doesn't answer in a channel | `/invite` it first. In channels it answers @mentions; DMs always work |
| In Studio, `/workspace/app` doesn't exist, or Patch ignores your instructions | Studio is on the `<name>--general-purpose` graph. Pick the graph named after your agent, then start a new thread |
| `uv run mda dev` fails with `project.dependencies[0]` must be pep508 | Your project path has a space in it (e.g. `starter copy`). Rename the folder without spaces, delete its `.venv` and `.mda` folders, and run again |
| A new file seems ignored | Restart `uv run mda dev`: new files are only picked up at startup |

## Going further

- **Each person's own GitHub.** Switch the connection to `{"type": "user"}`
  with an OAuth connection, and PRs open under each Slack user's own name. See
  [Connections](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections).
- **Skip retyping files.** `push_files` makes the model write out every changed
  file in full. An authored tool can read them straight from the sandbox via
  `runtime.backend`.
- **Prove it keeps working.** Add Harbor evals under `evals/tasks/`: the bug
  board makes a ready-made test set.
- **Call it from Claude Code** through its MCP endpoint.
