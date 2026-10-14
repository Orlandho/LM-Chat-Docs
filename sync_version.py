# -*- coding: utf-8 -*-
"""
LM-Chat™ Cross-Repository SemVer 2.0.0 Synchronization Utility.
Ensures 100% version synchronization between the LM-Chat extension codebase
and the LM-Chat-Docs documentation repository.
"""

import sys
import os
import re
import argparse
import datetime
import io
from typing import Dict, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DOCS_ROOT = os.path.abspath(os.path.dirname(__file__))

DOCS_VERSIONED_FILES = {
    "pyproject": {
        "path": os.path.join(DOCS_ROOT, "pyproject.toml"),
        "pattern": r'(^version\s*=\s*")([^"]+)(")',
        "replace": r'\g<1>{new_version}\g<3>',
    },
    "citation": {
        "path": os.path.join(DOCS_ROOT, "CITATION.cff"),
        "pattern": r'(^version:\s*)([^\r\n]+)',
        "replace": r'\g<1>{new_version}',
    },
    "readme": {
        "path": os.path.join(DOCS_ROOT, "README.md"),
        "pattern": r'(<!-- VERSION -->v)([^<]+)(<!-- /VERSION -->)',
        "replace": r'\g<1>{new_version}\g<3>',
    }
}


def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath: str, content: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def get_docs_version() -> str:
    versions = {}
    for name, target in DOCS_VERSIONED_FILES.items():
        if not os.path.exists(target["path"]):
            continue
        content = read_file(target["path"])
        match = re.search(target["pattern"], content, re.MULTILINE)
        if match:
            versions[name] = match.group(2).strip()
        else:
            raise ValueError(f"Could not extract version from {target['path']}")

    unique_versions = set(versions.values())
    if len(unique_versions) > 1:
        raise RuntimeError(f"Asynchronous versions detected within docs repository: {versions}")
    return list(unique_versions)[0]


def get_extension_version(repo_path: str) -> str:
    extension_toml = os.path.join(repo_path, "config", "extension.toml")
    if not os.path.exists(extension_toml):
        raise FileNotFoundError(f"Cannot find config/extension.toml at {repo_path}")
    content = read_file(extension_toml)
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not extract version from {extension_toml}")
    return match.group(1).strip()


def update_docs_version(new_version: str, dry_run: bool = False) -> None:
    today_str = datetime.date.today().isoformat()
    for name, target in DOCS_VERSIONED_FILES.items():
        filepath = target["path"]
        if not os.path.exists(filepath):
            continue
        content = read_file(filepath)
        updated = re.sub(
            target["pattern"],
            target["replace"].format(new_version=new_version),
            content,
            flags=re.MULTILINE
        )

        if name == "citation":
            updated = re.sub(
                r'(^date-released:\s*)([^\r\n]+)',
                rf'\g<1>{today_str}',
                updated,
                flags=re.MULTILINE
            )

        if dry_run:
            print(f"[Dry Run] Would update {os.path.relpath(filepath, DOCS_ROOT)} -> v{new_version}")
        else:
            write_file(filepath, updated)
            print(f"[✓] Updated {os.path.relpath(filepath, DOCS_ROOT)} -> v{new_version}")


def main():
    parser = argparse.ArgumentParser(description="LM-Chat Docs Version Synchronization Tool")
    parser.add_argument("--check", action="store_true", help="Verify docs version sanity")
    parser.add_argument("--target-repo", type=str, default="", help="Path to LM-Chat extension repository")
    parser.add_argument("--sync", action="store_true", help="Sync docs version from target extension repo")
    parser.add_argument("--set-version", type=str, default="", help="Manually set docs version")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without writing")

    args = parser.parse_args()

    current_docs_ver = get_docs_version()
    print(f"[*] Current LM-Chat-Docs version: v{current_docs_ver}")

    if args.target_repo:
        ext_ver = get_extension_version(args.target_repo)
        print(f"[*] Target Extension repository version: v{ext_ver}")
        if ext_ver != current_docs_ver:
            print(f"[!] Warning: Version mismatch! Extension=v{ext_ver}, Docs=v{current_docs_ver}")
            if args.sync:
                print(f"[*] Synchronizing Docs to v{ext_ver}...")
                update_docs_version(ext_ver, dry_run=args.dry_run)
                return 0
        else:
            print("[✓] Versions are 100% synchronized.")

    if args.set_version:
        update_docs_version(args.set_version, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
