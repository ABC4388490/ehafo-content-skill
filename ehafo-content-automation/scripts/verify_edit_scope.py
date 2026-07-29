#!/usr/bin/env python3
"""Snapshot and verify an exact edit allowlist with locked assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def write_result(ok: bool, errors: list[str]) -> int:
    print(json.dumps({"ok": ok, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("root", type=Path)
    snapshot_parser.add_argument("--output", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("root", type=Path)
    verify_parser.add_argument("--baseline", type=Path, required=True)
    verify_parser.add_argument("--allow", action="append", default=[])
    verify_parser.add_argument("--lock", action="append", default=[])

    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        return write_result(False, ["root_must_be_directory"])

    if args.command == "snapshot":
        args.output.write_text(
            json.dumps(manifest(root), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return write_result(True, [])

    try:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return write_result(False, [f"invalid_baseline:{exc}"])
    if not isinstance(baseline, dict):
        return write_result(False, ["baseline_must_be_object"])

    current = manifest(root)
    changed = {
        path for path in set(baseline) | set(current)
        if baseline.get(path) != current.get(path)
    }
    allowed = set(args.allow)
    errors = [
        f"changed_outside_allowlist:{path}"
        for path in sorted(changed - allowed)
    ]
    locks: dict[str, str] = {}
    for value in args.lock:
        path, separator, expected = value.rpartition("=")
        if not separator or len(expected) != 64:
            errors.append(f"invalid_lock_spec:{value}")
            continue
        locks[path] = expected.lower()
    for path, expected in sorted(locks.items()):
        if path not in baseline:
            errors.append(f"locked_asset_missing_from_baseline:{path}")
        elif path not in current:
            errors.append(f"locked_asset_missing_from_current:{path}")
        elif baseline[path] != current[path]:
            errors.append(f"locked_asset_changed:{path}")
        elif current[path].lower() != expected:
            errors.append(f"locked_asset_checksum_mismatch:{path}")
    return write_result(not errors, errors)


if __name__ == "__main__":
    sys.exit(main())
