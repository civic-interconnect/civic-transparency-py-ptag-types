#!/usr/bin/env python3
"""
Check that generated types are up-to-date with the spec.
Works in both pre-commit and CI environments.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Union, List
import filecmp


def run_command(cmd: list[str], cwd: str | None = None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def compare_directories(dir1: Union[str, Path], dir2: Union[str, Path]) -> bool:
    """Compare two directories and return True if they're identical, ignoring _version.py."""

    def compare_files(dcmp: filecmp.dircmp):
        # Filter out _version.py files from comparison
        left_only_filtered = [
            f for f in dcmp.left_only if isinstance(f, str) and f != "_version.py"
        ]
        right_only_filtered = [
            f for f in dcmp.right_only if isinstance(f, str) and f != "_version.py"
        ]
        diff_files_filtered = [
            f for f in dcmp.diff_files if isinstance(f, str) and f != "_version.py"
        ]

        if left_only_filtered or right_only_filtered or diff_files_filtered:
            return False
        for sub_dcmp in dcmp.subdirs.values():
            sub_dcmp: filecmp.dircmp
            if not compare_files(sub_dcmp):
                return False
        return True

    dcmp = filecmp.dircmp(dir1, dir2)
    return compare_files(dcmp)


def get_file_differences(dir1: Union[str, Path], dir2: Union[str, Path]) -> List[str]:
    """Get a list of differences between directories."""
    import filecmp

    differences = []

    def collect_diffs(dcmp: filecmp.dircmp, path: str = ""):
        for name in dcmp.left_only:
            differences.append(f"Only in current: {path}/{str(name)}")
        for name in dcmp.right_only:
            differences.append(f"Only in regenerated: {path}/{str(name)}")
        for name in dcmp.diff_files:
            differences.append(f"Modified: {path}/{str(name)}")
        for sub_name, sub_dcmp in dcmp.subdirs.items():
            sub_dcmp: filecmp.dircmp  # type: ignore
            collect_diffs(sub_dcmp, f"{path}/{sub_name}")

    dcmp = filecmp.dircmp(dir1, dir2)
    collect_diffs(dcmp)
    return differences


def main():
    """Check if generated types are up-to-date."""
    print("Checking if generated types are current...")

    repo_root = Path(__file__).parent.parent.parent
    types_dir = repo_root / "src" / "ci" / "transparency" / "types"
    generate_script = repo_root / "scripts" / "generate_types.py"

    if not types_dir.exists():
        print("ERROR: Types directory not found")
        return 1

    if not generate_script.exists():
        print("ERROR: generate_types.py script not found")
        return 1

    # Create temporary directory for regenerated types
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_types_dir = Path(temp_dir) / "types"
        temp_types_dir.mkdir(parents=True)

        # Copy current types to temp for comparison
        current_types_backup = Path(temp_dir) / "current_types"
        shutil.copytree(types_dir, current_types_backup)

        # Regenerate types
        print("Regenerating types...")
        success, _stdout, stderr = run_command(
            [sys.executable, str(generate_script)], cwd=str(repo_root)
        )

        if not success:
            print("ERROR: Failed to regenerate types:")
            print(stderr)
            return 1

        # Compare current types with backup
        if compare_directories(types_dir, current_types_backup):
            print("PASS: Generated types are up-to-date")
            return 0
        else:
            print("FAIL: Generated types are out of sync!")
            print("   The following differences were found:")

            differences = get_file_differences(current_types_backup, types_dir)
            for diff in differences[:10]:  # Show first 10 differences
                print(f"     {diff}")

            if len(differences) > 10:
                print(f"     ... and {len(differences) - 10} more differences")

            print()
            print("   To fix this, run:")
            print("     python scripts/generate_types.py")
            print("     git add src/ci/transparency/types/")

            return 1


if __name__ == "__main__":
    sys.exit(main())
