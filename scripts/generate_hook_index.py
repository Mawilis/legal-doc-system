#!/usr/bin/env python3
# DEPRECATED: Use `tools/repository/repository_analyzer.py` instead
import pathlib
import re

def find_hooks(root_dir):
    hooks = []
    for path in root_dir.rglob("*.jsx"):
        if path.is_file():
            with open(path, "r") as file:
                content = file.read()
                hook_matches = re.findall(r"const\s+(\w+)\s*=\s*React\.use", content)
                hooks.extend(hook_matches)
    return hooks

root_dir = pathlib.Path("/Users/wilsonkhanyezi/legal-doc-system")
hooks = find_hooks(root_dir)

with open("engineering/genome/HOOK_INDEX.md", "w") as file:
    file.write("# HOOK_INDEX.md\n\n")
    for hook in hooks:
        file.write(f"- {hook}\n")