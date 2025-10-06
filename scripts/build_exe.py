"""Build standalone Windows executable using PyInstaller."""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Build executable for Windows."""
    print("=" * 80)
    print("Building Movies Pipeline Windows Executable")
    print("=" * 80)

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Install it with: poetry add --group dev pyinstaller")
        sys.exit(1)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=movies-pipeline",
        "--onefile",  # Single executable
        "--console",  # Console application
        "--clean",  # Clean cache
        "--noconfirm",  # Overwrite without asking
        # Add data files
        "--add-data=.env.example;.",
        # Hidden imports
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=pyarrow",
        "--hidden-import=kaggle",
        # Entry point
        "src/main.py",
    ]

    print("\nBuilding executable...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 80)
        print("✓ Build successful!")
        print("=" * 80)
        print(f"\nExecutable location: {project_root / 'dist' / 'movies-pipeline.exe'}")
        print("\nTo run:")
        print("  .\\dist\\movies-pipeline.exe")
        print("\nTo run specific stage:")
        print("  .\\dist\\movies-pipeline.exe --stage ingestion")
        print("=" * 80)

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 80)
        print("✗ Build failed!")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

