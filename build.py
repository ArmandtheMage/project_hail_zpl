"""
Script to create the executable with PyInstaller.
Automatically scans project folders and includes them in the build.
"""
import os
import subprocess
import sys

# Project root folder
ROOT = os.path.dirname(os.path.abspath(__file__))

# Folders to include as data (modules + resources)
FOLDERS_TO_INCLUDE = ["azure_project", "export", "gui"]

# Folders/files to exclude from scanning
EXCLUDED = {"__pycache__", ".git", "build", "dist", "venv", ".venv", "env", "version"}

# Read version from file
VERSION_FILE = os.path.join(ROOT, "version")
with open(VERSION_FILE, "r") as f:
    VERSION = f.read().strip()

# Final executable name (with version)
EXE_NAME = f"HailZPL_v{VERSION}"

# Entry point
ENTRY_POINT = "run.py"


def find_data():
    """Scan FOLDERS_TO_INCLUDE and return a list of '--add-data' arguments
    for PyInstaller, each mapping a local folder to its relative destination."""
    add_data = []
    for folder in FOLDERS_TO_INCLUDE:
        path = os.path.join(ROOT, folder)
        if os.path.isdir(path):
            # Add the entire folder with its relative path
            add_data.append(f"{path}{os.pathsep}{folder}")
    return add_data


def find_hidden_imports():
    """Discover all .py modules inside FOLDERS_TO_INCLUDE and return them
    as fully-qualified module names for PyInstaller's --hidden-import flag."""
    hidden = []
    for folder in FOLDERS_TO_INCLUDE:
        path = os.path.join(ROOT, folder)
        if not os.path.isdir(path):
            continue
        for file in os.listdir(path):
            if file.endswith(".py") and file != "__init__.py":
                module = f"{folder}.{file[:-3]}"
                hidden.append(module)
    return hidden


def build():
    """Assemble the PyInstaller command and execute it.
    Returns the process exit code (0 on success)."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", EXE_NAME,
    ]

    # Add data
    for data in find_data():
        cmd.extend(["--add-data", data])

    # Add hidden imports
    for module in find_hidden_imports():
        cmd.extend(["--hidden-import", module])

    # Entry point
    cmd.append(os.path.join(ROOT, ENTRY_POINT))

    print("PyInstaller command:")
    print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
    print()

    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        print(f"\nBuild completed! Executable at: dist/{EXE_NAME}.exe")
    else:
        print(f"\nBuild error (exit code: {result.returncode})")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
