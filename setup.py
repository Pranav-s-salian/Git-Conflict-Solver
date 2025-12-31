from setuptools import setup, find_packages

setup(
    name="git-conflict-solver",
    version="2.0.0",
    description="Interactive CLI tool to automatically resolve git merge conflicts",
    author="Your Name",
    packages=find_packages(),
    py_modules=["cli_shell", "git_cli", "git_utils", "conflict_solver", "utils"],
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "git-solver=cli_shell:main",
            "git-conflict-solver=cli_shell:main",
        ],
    },
    python_requires=">=3.6",
)
