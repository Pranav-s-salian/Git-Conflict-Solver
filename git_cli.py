import click
from git_utils import run_git, run_git_merge, has_conflicts, is_git_repo, has_uncommitted_changes, stash_changes, unstash_changes, branch_exists, cleanup_lock_files, get_origin_url, set_origin_url
from conflict_solver import resolve_conflicts

@click.command()
def start():
    click.echo("🚀 Git Conflict Solver")
    click.echo("=" * 40)
    
    if not is_git_repo():
        click.echo("❌ Error: Current directory is not a git repository")
        click.echo("Please run this script from within a git repository")
        return
    
    # Check and setup origin remote
    current_origin = get_origin_url()
    if current_origin:
        click.echo(f"📡 Current origin: {current_origin}")
        if not click.confirm("Use this origin?", default=True):
            origin_url = click.prompt("Enter new origin URL")
            set_origin_url(origin_url)
            click.echo("✅ Origin updated")
    else:
        click.echo("⚠️  No origin remote found")
        origin_url = click.prompt("Enter origin remote URL")
        set_origin_url(origin_url)
        click.echo("✅ Origin added")
    
    click.echo("")
    friend_branch = click.prompt("Enter FRIEND branch name")
    your_branch = click.prompt("Enter YOUR branch name")
    proceed = click.confirm("Proceed with merge?", default=True)

    if not proceed:
        click.echo("❌ Merge cancelled")
        return

    stashed = False
    try:
        # Clean up any stale lock files
        if cleanup_lock_files():
            click.echo("🧹 Cleaned up stale git lock files...")
        
        # Check for uncommitted changes and stash them
        if has_uncommitted_changes():
            click.echo("📦 Stashing uncommitted changes...")
            stash_changes()
            stashed = True
        
        run_git("fetch origin")
        
        # Validate branches exist
        your_branch_ref = branch_exists(your_branch)
        friend_branch_ref = branch_exists(friend_branch)
        
        if not your_branch_ref:
            raise RuntimeError(f"Branch '{your_branch}' not found locally or on origin")
        if not friend_branch_ref:
            raise RuntimeError(f"Branch '{friend_branch}' not found locally or on origin")
        
        click.echo(f"📍 Found your branch: {your_branch_ref}")
        click.echo(f"📍 Found friend branch: {friend_branch_ref}")
        
        run_git("checkout main")
        run_git("pull origin main")
        
        # Delete integration branch if it exists from a previous run
        try:
            run_git("branch -D auto-integration-branch")
        except:
            pass  # Branch doesn't exist, that's fine
            
        run_git("checkout -b auto-integration-branch")

        click.echo("🔀 Merging your branch...")
        has_conflicts_your = run_git_merge(your_branch_ref)
        
        if has_conflicts_your:
            click.echo("🛠 Resolving conflicts from your branch...")
            resolve_conflicts()
            run_git("add -A")
            run_git("commit --no-edit")

        click.echo("🔀 Merging friend branch...")
        has_conflicts_friend = run_git_merge(friend_branch_ref)

        if has_conflicts_friend:
            click.echo("🛠 Resolving conflicts from friend branch...")
            resolve_conflicts()
            run_git("add -A")
            run_git("commit --no-edit")

        run_git("checkout main")
        run_git("merge auto-integration-branch")
        run_git("push origin main")

        click.echo("✅ Successfully merged branches into main")
        
        # Restore stashed changes if any
        if stashed:
            click.echo("📦 Restoring your stashed changes...")
            unstash_changes()
            
    except RuntimeError as e:
        click.echo(f"❌ Error: {str(e)}")
        # Try to restore stashed changes even on error
        if stashed:
            try:
                click.echo("📦 Restoring your stashed changes...")
                unstash_changes()
            except:
                click.echo("⚠️ Warning: Could not restore stashed changes. Run 'git stash pop' manually.")
        return

if __name__ == "__main__":
    start()
