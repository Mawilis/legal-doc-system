#!/usr/bin/env python3
# DEPRECATED: Use `tools/repository/repository_analyzer.py` instead
import pathlib
import re

def find_components(root_dir):
    components = []
    for path in root_dir.rglob("*.jsx"):
        if path.is_file():
            with open(path, "r") as file:
                content = file.read()
                component_matches = re.findall(r"const\s+(\w+)\s*=\s*React\.forwardRef", content)
                components.extend(component_matches)
    return components

root_dir = pathlib.Path("/Users/wilsonkhanyezi/legal-doc-system")
components = find_components(root_dir)

with open("engineering/genome/COMPONENT_INDEX.md", "w") as file:
    file.write("# COMPONENT_INDEX.md\n\n")
    for component in components:
        file.write(f"- {component}\n")