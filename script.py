from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import subprocess

from git import Repo

# Constants.
INITIAL_COMMIT = "4f475c7697722e946e39e42f38f3dd03a95d8765"
START_DATE = date(2014, 8, 12)
SYNAPSE_DIR = Path(".") / "synapse"

# Start at the nearest Monday.
day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
while day.weekday():
    day -= timedelta(days=1)

repo = Repo(SYNAPSE_DIR)


def search(string):
    result = subprocess.run(
        ["grep", "-r", string, "synapse"],
        capture_output=True,
        cwd=SYNAPSE_DIR)

    total = 0
    by_module = defaultdict(int)
    for line in result.stdout.splitlines():
        line = line.decode("ascii")
        filename, match = line.split(":", 1)
        module = "/".join(filename.split("/", 2)[:2])
        total += 1
        by_module[module] += 1

    return total, by_module


# Iterate from the newest to the oldest commit.
data = []
for commit in repo.iter_commits("develop"):
    # Get the commit at the start of the day.
    committed_date = datetime.fromtimestamp(commit.committed_date)
    if committed_date < day:
        # The next date will be a week in the past.
        day -= timedelta(days=7 )

        # Checkout this commit (why is this so hard?).
        repo.head.reference = commit
        repo.head.reset(index=True, working_tree=True)

        # Find the number of inlineCallback functions.
        deferred_result = search("inlineCallback")

        # Find the number of async functions.
        async_result = search("async def")

        print(commit, deferred_result[0], async_result[0])

        data.append((commit.hexsha, str(committed_date), deferred_result, async_result))

with open("results.json", "w") as f:
    f.write(json.dumps(data))
