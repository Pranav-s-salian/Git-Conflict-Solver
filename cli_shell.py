import os
import sys
from pathlib import Path
import click
from git_utils import (
    run_git, run_git_merge, has_conflicts, is_git_repo, 
    has_uncommitted_changes, stash_changes, unstash_changes, 
    branch_exists, cleanup_lock_files, get_origin_url, set_origin_url
)
from conflict_solver import resolve_conflicts

class ConflictSolverShell:
    def __init__(self):
        self.origin_url = None
        self.running = True
        
    def print_banner(self):
        click.echo("=" * 60)
        click.echo("🚀 GIT CONFLICT SOLVER - Interactive CLI")
        click.echo("=" * 60)
        click.echo("Type 'help' to see available commands")
        click.echo("Type 'exit' to quit")
        click.echo("=" * 60)
        click.echo()
        
    def print_help(self):
        click.echo("\n📖 Available Commands:")
        click.echo("-" * 60)
        click.echo("  cd <path>      - Change working directory")
        click.echo("  pwd            - Show current working directory")
        click.echo("  ls             - List items in current directory")
        click.echo("  setup          - Configure origin remote URL")
        click.echo("  merge          - Merge two branches with auto conflict resolution")
        click.echo("  status         - Show git repository status")
        click.echo("  branches       - List all branches (local and remote)")
        click.echo("  stash          - Stash uncommitted changes")
        click.echo("  unstash        - Restore stashed changes")
        click.echo("  cleanup        - Remove stale git lock files")
        click.echo("  help           - Show this help message")
        click.echo("  exit           - Exit the program")
        click.echo("-" * 60)
        click.echo()

    def prompt_prefix(self) -> str:
        # Show current working directory in prompt for navigation clarity
        cwd = Path(os.getcwd())
        return f"git-solver ({cwd})>"

    def cmd_cd(self, target: str):
        """Change working directory (cd)."""
        try:
            if not target.strip():
                # Behave like printing current dir if no path provided
                click.echo(Path(os.getcwd()))
                return

            new_path = Path(target).expanduser()
            if not new_path.is_absolute():
                new_path = (Path(os.getcwd()) / new_path).resolve()
            else:
                new_path = new_path.resolve()

            if not new_path.exists() or not new_path.is_dir():
                click.echo(f"❌ Path not found: {new_path}")
                return

            os.chdir(new_path)
            click.echo(f"📂 Now in: {new_path}")
        except Exception as e:
            click.echo(f"❌ Error changing directory: {e}")

    def cmd_ls(self):
        """List files/folders in the current directory."""
        try:
            cwd = Path(os.getcwd())
            entries = sorted(cwd.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            if not entries:
                click.echo("(empty)")
                return
            for entry in entries:
                suffix = "/" if entry.is_dir() else ""
                click.echo(f"{entry.name}{suffix}")
        except Exception as e:
            click.echo(f"❌ Error listing directory: {e}")
        
    def cmd_setup(self):
        """Setup origin remote URL"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        current_origin = get_origin_url()
        if current_origin:
            click.echo(f"📡 Current origin: {current_origin}")
            if click.confirm("Change origin URL?", default=False):
                new_url = click.prompt("Enter new origin URL")
                set_origin_url(new_url)
                click.echo("✅ Origin updated successfully")
        else:
            click.echo("⚠️  No origin remote found")
            new_url = click.prompt("Enter origin URL")
            set_origin_url(new_url)
            click.echo("✅ Origin added successfully")
            
    def cmd_merge(self):
        """Perform merge with auto conflict resolution"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        # Check origin
        if not get_origin_url():
            click.echo("⚠️  No origin remote configured")
            if click.confirm("Set up origin now?", default=True):
                self.cmd_setup()
            else:
                return
                
        friend_branch = click.prompt("Enter FRIEND branch name")
        your_branch = click.prompt("Enter YOUR branch name")
        
        if not click.confirm("Proceed with merge?", default=True):
            click.echo("❌ Merge cancelled")
            return
            
        stashed = False
        try:
            # Clean up lock files
            if cleanup_lock_files():
                click.echo("🧹 Cleaned up stale git lock files")
                
            # Stash changes
            if has_uncommitted_changes():
                click.echo("📦 Stashing uncommitted changes...")
                stash_changes()
                stashed = True
                
            click.echo("🔄 Fetching from origin...")
            run_git("fetch origin")
            
            # Validate branches
            your_branch_ref = branch_exists(your_branch)
            friend_branch_ref = branch_exists(friend_branch)
            
            if not your_branch_ref:
                raise RuntimeError(f"Branch '{your_branch}' not found")
            if not friend_branch_ref:
                raise RuntimeError(f"Branch '{friend_branch}' not found")
                
            click.echo(f"📍 Found your branch: {your_branch_ref}")
            click.echo(f"📍 Found friend branch: {friend_branch_ref}")
            
            run_git("checkout main")
            run_git("pull origin main")
            
            # Delete old integration branch
            try:
                run_git("branch -D auto-integration-branch")
            except:
                pass
                
            run_git("checkout -b auto-integration-branch")
            
            # Merge your branch
            click.echo("🔀 Merging your branch...")
            has_conflicts_your = run_git_merge(your_branch_ref)
            
            if has_conflicts_your:
                click.echo("🛠 Resolving conflicts from your branch...")
                resolve_conflicts()
                run_git("add -A")
                run_git("commit --no-edit")
                
            # Merge friend branch
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
            
            if stashed:
                click.echo("📦 Restoring your stashed changes...")
                unstash_changes()
                
        except RuntimeError as e:
            click.echo(f"❌ Error: {str(e)}")
            if stashed:
                try:
                    click.echo("📦 Restoring your stashed changes...")
                    unstash_changes()
                except:
                    click.echo("⚠️  Could not restore stashed changes. Run 'git stash pop' manually.")
                    
    def cmd_status(self):
        """Show git status"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        try:
            result = run_git("status")
            click.echo(result.stdout)
        except RuntimeError as e:
            click.echo(f"❌ Error: {str(e)}")
            
    def cmd_branches(self):
        """List all branches"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        try:
            click.echo("\n📋 Local Branches:")
            result = run_git("branch")
            click.echo(result.stdout)
            
            click.echo("\n📋 Remote Branches:")
            result = run_git("branch -r")
            click.echo(result.stdout)
        except RuntimeError as e:
            click.echo(f"❌ Error: {str(e)}")
            
    def cmd_stash(self):
        """Stash uncommitted changes"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        if has_uncommitted_changes():
            try:
                stash_changes()
                click.echo("✅ Changes stashed successfully")
            except RuntimeError as e:
                click.echo(f"❌ Error: {str(e)}")
        else:
            click.echo("ℹ️  No uncommitted changes to stash")
            
    def cmd_unstash(self):
        """Restore stashed changes"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        try:
            unstash_changes()
            click.echo("✅ Stashed changes restored")
        except RuntimeError as e:
            click.echo(f"❌ Error: {str(e)}")
            
    def cmd_cleanup(self):
        """Remove stale git lock files"""
        if not is_git_repo():
            click.echo("❌ Not a git repository")
            return
            
        if cleanup_lock_files():
            click.echo("✅ Cleaned up stale git lock files")
        else:
            click.echo("ℹ️  No lock files found")
            
    def run(self):
        """Run the interactive shell"""
        self.print_banner()
        
        # Check if in git repo
        if not is_git_repo():
            click.echo("⚠️  Warning: Current directory is not a git repository")
            click.echo("Navigate to a git repository to use git commands")
            click.echo()
            
        while self.running:
            try:
                command = click.prompt(f"\n{self.prompt_prefix()}", default="", show_default=False)
                command = command.strip()
                lowered = command.lower()
                
                if not command:
                    continue
                    
                if lowered.startswith("cd"):
                    parts = command.split(maxsplit=1)
                    path_arg = parts[1] if len(parts) > 1 else ""
                    self.cmd_cd(path_arg)
                elif lowered == "ls":
                    self.cmd_ls()
                elif lowered == "pwd":
                    click.echo(Path(os.getcwd()))
                elif lowered == "help":
                    self.print_help()
                elif lowered == "exit" or lowered == "quit":
                    click.echo("👋 Goodbye!")
                    self.running = False
                elif lowered == "setup":
                    self.cmd_setup()
                elif lowered == "merge":
                    self.cmd_merge()
                elif lowered == "status":
                    self.cmd_status()
                elif lowered == "branches":
                    self.cmd_branches()
                elif lowered == "stash":
                    self.cmd_stash()
                elif lowered == "unstash":
                    self.cmd_unstash()
                elif lowered == "cleanup":
                    self.cmd_cleanup()
                else:
                    click.echo(f"❌ Unknown command: '{command}'")
                    click.echo("Type 'help' to see available commands")
                    
            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                self.running = False
            except EOFError:
                click.echo("\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                click.echo(f"❌ Error: {str(e)}")

@click.command()
def main():
    """Git Conflict Solver - Interactive CLI"""
    shell = ConflictSolverShell()
    shell.run()

if __name__ == "__main__":
    main()
