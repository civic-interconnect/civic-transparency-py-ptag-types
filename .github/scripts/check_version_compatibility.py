#!/usr/bin/env python3
"""
Version compatibility checking for civic transparency types.
Works in both pre-commit and CI environments.
"""

import sys
from pathlib import Path
from typing import Optional

# Add src to path so we can import from development installation
repo_root = Path(__file__).parent.parent.parent
src_path = repo_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("ERROR: Neither tomllib nor tomli available")
        sys.exit(1)


def get_types_version():
    """Get the current types package version."""
    try:
        from ci.transparency.types import __version__

        return __version__
    except ImportError:
        # Try importlib.metadata if package is installed
        try:
            from importlib.metadata import version

            return version("civic-transparency-types")
        except ImportError:
            try:
                import pkg_resources

                return pkg_resources.get_distribution(
                    "civic-transparency-types"
                ).version
            except Exception:
                pass
        except Exception:
            pass

        print("INFO: civic-transparency-types not installed (using development mode)")
        return "dev"


def get_installed_spec_version() -> Optional[str]:
    """Get the currently installed spec version."""
    try:
        import ci.transparency.spec

        # Try multiple ways to get version
        if hasattr(ci.transparency.spec, "__version__"):
            return ci.transparency.spec.__version__

        # Try importlib.metadata (modern Python)
        try:
            from importlib.metadata import version

            return version("civic-transparency-spec")
        except ImportError:
            # Fallback for older Python
            try:
                import pkg_resources

                return pkg_resources.get_distribution("civic-transparency-spec").version
            except Exception:
                pass

        # Try reading _version.py directly
        try:
            from ci.transparency.spec._version import __version__

            return __version__
        except ImportError:
            pass

        print("INFO: civic-transparency-spec installed but version not accessible")
        return "unknown"

    except ImportError:
        return None


def get_declared_spec_version():
    """Get spec version from pyproject.toml if explicitly pinned."""
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return None

    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])

    for dep in dev_deps:
        if dep.startswith("civic-transparency-spec=="):
            return dep.split("==")[1]

    return None


def main():
    """Check version compatibility."""
    print("Checking version compatibility...")

    types_ver = get_types_version()
    spec_ver = get_installed_spec_version()
    declared_spec_ver = get_declared_spec_version()

    print(f"Types version: {types_ver}")

    if not spec_ver:
        print("ERROR: civic-transparency-spec not installed")
        if declared_spec_ver:
            print(f"   Run: pip install civic-transparency-spec=={declared_spec_ver}")
        else:
            print("   Run: pip install 'civic-transparency-spec>=0.2.0'")
        return 1

    print(f"Installed spec version: {spec_ver}")
    if declared_spec_ver:
        print(f"Declared spec version: {declared_spec_ver}")

    # Check if declared version matches installed (if declared)
    if declared_spec_ver and declared_spec_ver != spec_ver:
        print(
            f"FAIL: Declared spec version ({declared_spec_ver}) != installed ({spec_ver})"
        )
        print(f"   Run: pip install civic-transparency-spec=={declared_spec_ver}")
        return 1

    # For development mode, be more permissive
    if types_ver == "dev" or "dev" in types_ver:
        if spec_ver:
            print("PASS: Development mode with spec installed")
            return 0

    # Simple major.minor compatibility check for release versions
    if types_ver != "dev" and spec_ver and "dev" not in types_ver:
        try:
            types_parts = [int(x) for x in types_ver.split(".dev")[0].split(".")]
            spec_parts = [int(x) for x in spec_ver.split(".dev")[0].split(".")]

            if len(types_parts) >= 2 and len(spec_parts) >= 2:
                if types_parts[0] == spec_parts[0] and types_parts[1] == spec_parts[1]:
                    print("PASS: Versions are compatible")
                    return 0
                else:
                    print(
                        f"FAIL: Version incompatibility - Types {types_ver} vs Spec {spec_ver}"
                    )
                    print("   Consider tagging repository to match spec version:")
                    print(f"   git tag v{spec_ver} -m 'Release {spec_ver}'")
                    return 1
        except (ValueError, IndexError):
            pass

    print("PASS: Basic compatibility check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
