from collections import defaultdict, namedtuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import subprocess

from git import Repo

Project = namedtuple("Project", ("name", "initial_commit", "branch", "paths"))

# Constants.
PROJECTS = (
    Project("synapse", "4f475c7697722e946e39e42f38f3dd03a95d8765", "develop", ("synapse", "tests", "contrib", "docs", "scripts")),
    Project("sydent", "2360cd427fb5cbebd34baa02ccb05ca2211eab63", "main", ("sydent", "tests", "matrix_is_test", "docs", "scripts")),
    Project("sygnal", "2eb2dd4eb6d83a17f260af02731940427e67feea", "main", ("sygnal", "tests", "docs")),
)

# Start at the nearest Monday.
LATEST_MONDAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
while LATEST_MONDAY.weekday():
    LATEST_MONDAY -= timedelta(days=1)


def search(string, root, paths):
    result = subprocess.run(
        ["grep", "-rE", "\\b" + string + "\\b", *paths],
        capture_output=True,
        cwd=root)

    total = 0
    by_module = defaultdict(int)
    for line in result.stdout.splitlines():
        filename, match = line.split(b":", 1)
        filename = filename.decode("ascii")
        # Trim to the second-level module (e.g. foo.bar.* all gets grouped together).
        module = "/".join(filename.split("/", 2)[:2])
        # If there's a file extension, strip it off.
        module = module.split(".")[0]
        total += 1
        by_module[module] += 1

    return total, by_module


# The resulting output data.
#
# It is of the form of:
#
# {
#   "project": [
#     <commit hash>, <date as a string>, <inlineCallbacks results>, <Deferred results>, <async results>
#   ]
# }
#
# Each of the results is of the form:
#
# [
#   <total>,
#   {
#     <module name>: <count>
#   }
# ]
data = {}

for project in PROJECTS:
    project_dir = Path(".") / project.name
    repo = Repo(project_dir)

    print(project.name)

    # Fetch updated changes.
    origin = repo.remotes[0]
    origin.fetch()

    # Start at the latest monday.
    day = LATEST_MONDAY

    # Iterate from the newest to the oldest commit.
    project_data = []
    for it, commit in enumerate(repo.iter_commits("origin/" + project.branch)):
        # Get the commit at the start of the day.
        committed_date = datetime.fromtimestamp(commit.committed_date)
        # Always include the latest commit, the earliest commit, and the last commit
        # of each Sunday.
        if committed_date < day or commit.hexsha == project.initial_commit or it == 0:
            # The next date will be a week in the past, if this is not the initial
            # commit.
            if it != 0:
                day -= timedelta(days=7)

            # Checkout this commit (why is this so hard?).
            repo.head.reference = commit
            repo.head.reset(index=True, working_tree=True)

            # Find the number of inlineCallback functions.
            inlineCallbacks_result = search("(inlineCallbacks|cachedInlineCallbacks)", project_dir, project.paths)

            # Additional helpers.
            deferreds_results = search("(ensureDeferred|maybeDeferred|succeed|failure)\\(", project_dir, project.paths)

            # Find the number of async functions.
            async_result = search("async def", project_dir, project.paths)

            print(commit, inlineCallbacks_result[0], deferreds_results[0], async_result[0])

            project_data.append((
                commit.hexsha,
                str(committed_date),
                inlineCallbacks_result,
                deferreds_results,
                async_result,
            ))

    # Empty line.
    print()

    # Store the results.
    data[project.name] = project_data

# Output the results.
with open("results.json", "w") as f:
    f.write(json.dumps(data, indent=4))
