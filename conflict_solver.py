from pathlib import Path
import subprocess
from git_utils import GIT_EXECUTABLE

def resolve_conflicts():
    files = subprocess.check_output(
        f'"{GIT_EXECUTABLE}" diff --name-only --diff-filter=U',
        shell=True,
        text=True
    ).splitlines()

    for file in files:
        path = Path(file)
        content = path.read_text()

        resolved = []
        in_conflict = False

        for line in content.splitlines():
            if line.startswith("<<<<<<<"):
                in_conflict = True
                continue
            elif line.startswith("======="):
                continue
            elif line.startswith(">>>>>>>"):
                in_conflict = False
                continue

            resolved.append(line)

        path.write_text("\n".join(resolved))
