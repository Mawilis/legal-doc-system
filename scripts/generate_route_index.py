#!/usr/bin/env python3
# DEPRECATED: Use `tools/repository/repository_analyzer.py` instead
import pathlib
import re

def find_routes(root_dir):
    routes = []
    for path in root_dir.rglob("*.js"):
        if path.is_file():
            with open(path, "r") as file:
                content = file.read()
                route_matches = re.findall(r"(app|router|express)\.(get|post|put|delete|patch)\s*\(\s*['\"](.*?)['\"]", content)
                routes.extend(route_matches)
    return routes

root_dir = pathlib.Path("/Users/wilsonkhanyezi/legal-doc-system")
routes = find_routes(root_dir)

with open("engineering/genome/ROUTE_INDEX.md", "w") as file:
    file.write("# ROUTE_INDEX.md\n\n")
    for route in routes:
        file.write(f"- {route[0]}.{route[1]}('{route[2]}')\n")