# Git Conflict Solver

Interactive CLI tool to automatically merge branches and resolve conflicts - Node.js style!

## 🚀 Quick Installation

### Option 1: Double-click Install
1. Double-click `install.bat` in this folder
2. Wait for installation to complete
3. Done! You can now use `git-solver` from anywhere

### Option 2: Manual Install
```bash
pip install -e .
```

## 📖 Usage

### Start the Interactive CLI
```bash
# Navigate to any directory
cd path/to/your/folder

# Start the interactive CLI
git-solver
```

You'll see an interactive prompt:
```
============================================================
🚀 GIT CONFLICT SOLVER - Interactive CLI
============================================================
Type 'help' to see available commands
Type 'exit' to quit
============================================================

git-solver>
```

## 🎯 Available Commands

| Command   | Description                                      |
|-----------|--------------------------------------------------|
| `setup`   | Configure origin remote URL                      |
| `merge`   | Merge two branches with auto conflict resolution |
| `status`  | Show git repository status                       |
| `branches`| List all branches (local and remote)            |
| `stash`   | Stash uncommitted changes                        |
| `unstash` | Restore stashed changes                          |
| `cleanup` | Remove stale git lock files                      |
| `help`    | Show available commands                          |
| `exit`    | Exit the program                                 |

## ✨ Features

- 🎮 **Interactive CLI** - Node.js style command interface
- 🔧 **Auto conflict resolution** - Resolves merge conflicts automatically
- 📦 **Stash management** - Stash and restore changes with simple commands
- 🧹 **Lock file cleanup** - Remove stale git lock files
- 🌐 **Remote setup** - Easy origin URL configuration
- 🔍 **Branch validation** - Checks if branches exist
- ✅ **Safe operations** - Validates before making changes

## 📝 Example Session

```
git-solver> help
📖 Available Commands:
------------------------------------------------------------
  setup          - Configure origin remote URL
  merge          - Merge two branches with auto conflict resolution
  status         - Show git repository status
  branches       - List all branches (local and remote)
  stash          - Stash uncommitted changes
  unstash        - Restore stashed changes
  cleanup        - Remove stale git lock files
  help           - Show this help message
  exit           - Exit the program
------------------------------------------------------------

git-solver> setup
📡 Current origin: https://github.com/user/repo.git
Change origin URL? [y/N]: n

git-solver> merge
Enter FRIEND branch name: friend-branch
Enter YOUR branch name: your-branch
Proceed with merge? [Y/n]: y
📦 Stashing uncommitted changes...
🔄 Fetching from origin...
📍 Found your branch: your-branch
📍 Found friend branch: friend-branch
🔀 Merging your branch...
🔀 Merging friend branch...
🛠 Resolving conflicts from friend branch...
✅ Successfully merged branches into main
📦 Restoring your stashed changes...

git-solver> status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

git-solver> exit
👋 Goodbye!
```

## 🛠️ Requirements

- Python 3.6+
- Git installed on your system
- Click package (installed automatically)

## 📦 What the `merge` command does

1. Checks if you're in a git repository
2. Sets up origin remote (if needed)
3. Stashes any uncommitted changes
4. Creates a temporary integration branch
5. Merges your branch
6. Merges friend's branch
7. Resolves any conflicts automatically
8. Merges everything back to main
9. Pushes to origin
10. Restores your stashed changes

## ⚠️ Notes

- The CLI works from any directory, but git commands need a git repository
- Always review changes after automatic conflict resolution
- Creates a temporary branch called `auto-integration-branch`
- Your uncommitted changes are safely stashed and restored
- Works with both local and remote branches

## 🎨 Command Shortcuts

You can also run:
- `git-conflict-solver` (alternative command name)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
