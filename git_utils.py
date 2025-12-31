import subprocess
import os

# Try to find Git executable
GIT_EXECUTABLE = None
possible_paths = [
    "C:\\Program Files\\Git\\cmd\\git.exe",
    "C:\\Program Files (x86)\\Git\\cmd\\git.exe",
    "C:\\Git\\cmd\\git.exe"
]

for path in possible_paths:
    if os.path.exists(path):
        GIT_EXECUTABLE = path
        break

if not GIT_EXECUTABLE:
    GIT_EXECUTABLE = "git"  # Fallback to system PATH

def run_git(command):
    result = subprocess.run(f'"{GIT_EXECUTABLE}" {command}', shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(f"Git command failed: {error_msg}")
    return result

def run_git_merge(branch):
    """Run git merge, allowing conflicts (returns True if conflicts exist)"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" merge {branch} --no-edit',
        shell=True,
        capture_output=True,
        text=True
    )
    # Return code 1 with conflicts is OK, we'll resolve them
    if result.returncode != 0 and not has_conflicts():
        error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(f"Merge failed: {error_msg}")
    return has_conflicts()

def branch_exists(branch):
    """Check if a branch exists locally or remotely"""
    # Check local
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" rev-parse --verify {branch}',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return branch
    
    # Check remote
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" rev-parse --verify origin/{branch}',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return f"origin/{branch}"
    
    return None

def has_conflicts():
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" diff --name-only --diff-filter=U',
        shell=True,
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())

def is_git_repo():
    """Check if current directory is a git repository"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" rev-parse --git-dir',
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def get_git_dir():
    """Get the .git directory path"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" rev-parse --git-dir',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def cleanup_lock_files():
    """Remove stale git lock files that can block operations"""
    git_dir = get_git_dir()
    if git_dir:
        lock_file = os.path.join(git_dir, 'index.lock')
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                return True
            except:
                pass
    return False

def has_uncommitted_changes():
    """Check if there are uncommitted changes in the working directory"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" status --porcelain',
        shell=True,
        capture_output=True,
        text=True
    )
    return bool(result.stdout.strip())

def stash_changes():
    """Stash any uncommitted changes"""
    run_git("stash push -m 'git-conflict-solver-auto-stash'")
    return True

def unstash_changes():
    """Restore stashed changes if they exist"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" stash list',
        shell=True,
        capture_output=True,
        text=True
    )
    if 'git-conflict-solver-auto-stash' in result.stdout:
        run_git("stash pop")

def get_origin_url():
    """Get the current origin remote URL"""
    result = subprocess.run(
        f'"{GIT_EXECUTABLE}" remote get-url origin',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def set_origin_url(url):
    """Set or update the origin remote URL"""
    current_url = get_origin_url()
    if current_url:
        run_git(f"remote set-url origin {url}")
    else:
        run_git(f"remote add origin {url}")
    return True
