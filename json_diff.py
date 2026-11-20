#!/usr/bin/env python3
"""Diff two JSON files by key path.

Usage:
    python json_diff.py a.json b.json [--ignore-order] [--quiet]

Prints added, removed and changed keys as dotted paths, e.g.
    + user.email
    - settings.debug
    ~ config.timeout: 30 -> 60

Exit code 0 when the files are equal, 1 when they differ, 2 on error.
Zero dependencies, Python 3.8+.
"""

import argparse
import json
import sys


def flatten(value, prefix=""):
    """Flatten nested dicts/lists into {dotted.path: leaf_value}."""
    out = {}
    if isinstance(value, dict):
        if not value:
            out[prefix] = value
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(item, path))
    elif isinstance(value, list):
        if not value:
            out[prefix] = value
        for i, item in enumerate(value):
            path = f"{prefix}[{i}]" if prefix else f"[{i}]"
            out.update(flatten(item, path))
    else:
        out[prefix] = value
    return out


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def diff(a, b, ignore_order=False):
    """Return (added, removed, changed) lists of (path, old, new)."""
    if ignore_order:
        a = _sort_lists(a)
        b = _sort_lists(b)
    fa, fb = flatten(a), flatten(b)
    added = [(p, None, fb[p]) for p in sorted(set(fb) - set(fa))]
    removed = [(p, fa[p], None) for p in sorted(set(fa) - set(fb))]
    changed = [
        (p, fa[p], fb[p])
        for p in sorted(set(fa) & set(fb))
        if fa[p] != fb[p]
    ]
    return added, removed, changed


def _sort_lists(value):
    if isinstance(value, list):
        try:
            return sorted((_sort_lists(v) for v in value), key=repr)
        except TypeError:
            return [_sort_lists(v) for v in value]
    if isinstance(value, dict):
        return {k: _sort_lists(v) for k, v in value.items()}
    return value


def fmt(value):
    return json.dumps(value, ensure_ascii=False)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Diff two JSON files by key path."
    )
    parser.add_argument("file_a", help="first JSON file")
    parser.add_argument("file_b", help="second JSON file")
    parser.add_argument(
        "--ignore-order",
        action="store_true",
        help="ignore the order of list items",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only set the exit code, print nothing",
    )
    args = parser.parse_args(argv)

    a = load_json(args.file_a)
    b = load_json(args.file_b)
    added, removed, changed = diff(a, b, args.ignore_order)

    if not args.quiet:
        for path, _, new in added:
            print(f"+ {path}: {fmt(new)}")
        for path, old, _ in removed:
            print(f"- {path}: {fmt(old)}")
        for path, old, new in changed:
            print(f"~ {path}: {fmt(old)} -> {fmt(new)}")
        total = len(added) + len(removed) + len(changed)
        if total == 0:
            print("identical")
        else:
            print(
                f"{total} difference(s): "
                f"{len(added)} added, {len(removed)} removed, "
                f"{len(changed)} changed"
            )
    return 1 if (added or removed or changed) else 0


if __name__ == "__main__":
    sys.exit(main())
