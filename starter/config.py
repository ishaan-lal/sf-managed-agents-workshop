"""The one place that names the repo Patch works on.

The checkout middleware and the GitHub workaround import these, so nothing else
hardcodes your fork.
"""

import os

# TODO(step 1): replace "TODO" with the name of the .env key that holds your
# fork (owner/name). `uv run mda dev` loads .env, and `uv run mda deploy`
# forwards it to the deployment.
REPO = os.environ.get("TODO", "").strip()

# Where the repo is cloned inside each thread's sandbox.
CHECKOUT = "/workspace/app"
