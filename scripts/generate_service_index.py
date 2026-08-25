#!/usr/bin/env python3
# DEPRECATED: Use `tools/repository/repository_analyzer.py` instead
import pathlib
import re

def find_services(root_dir):
    services = []
    for path in root_dir.rglob("*.js"):
        if path.is_file():
            with open(path, "r") as file:
                content = file.read()
                service_matches = re.findall(r"class\s+(\w+)\s+extends\s+(\w+)", content)
                services.extend(service_matches)
    return services

root_dir = pathlib.Path("/Users/wilsonkhanyezi/legal-doc-system")
services = find_services(root_dir)

with open("engineering/genome/SERVICE_INDEX.md", "w") as file:
    file.write("# SERVICE_INDEX.md\n\n")
    for service in services:
        file.write(f"- {service[0]} extends {service[1]}\n")