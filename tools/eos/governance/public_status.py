"""Deterministic public-status renderer/checker for the GitHub governance plane."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; STATUS_PATH="tools/eos/governance/public_project_status.json"; README_PATH="README.md"
START="<!-- WILSY_PUBLIC_STATUS_START -->"; END="<!-- WILSY_PUBLIC_STATUS_END -->"; SCHEMA_VERSION=1
def parse_status(raw: str) -> dict[str, object]:
    data=json.loads(raw)
    if not isinstance(data,dict) or data.get("schema_version") != SCHEMA_VERSION: raise ValueError("unsupported public-status schema")
    if not isinstance(data.get("milestones"),list) or not isinstance(data.get("current_frontier"),str): raise ValueError("malformed public-status schema")
    return data
def canonical_status() -> dict[str, object]: return parse_status((ROOT/STATUS_PATH).read_text(encoding="utf-8"))
def render_block(status: dict[str, object]) -> str: return f"{START}\n```json\n{json.dumps(status,ensure_ascii=False,indent=2,sort_keys=True)}\n```\n{END}"
def validate_text(readme: str, status_raw: str) -> None:
    status=parse_status(status_raw); count_start=readme.count(START); count_end=readme.count(END)
    if count_start != 1 or count_end != 1: raise ValueError("public-status markers must occur exactly once")
    before, _, rest=readme.partition(START); body, sep, after=rest.partition(END)
    if not sep or START in body or END in after: raise ValueError("reversed or nested public-status markers")
    if before is None: raise ValueError("missing public-status prefix")
    if START+body+END != render_block(status): raise ValueError("README public-status drift")
def read_authority(surface: str) -> tuple[str,str]:
    if surface=="worktree": return (README_PATH and (ROOT/README_PATH).read_text(encoding="utf-8"),(ROOT/STATUS_PATH).read_text(encoding="utf-8"))
    if surface=="index":
        read=lambda p: subprocess.check_output(["git","-C",str(ROOT),"show",f":{p}",],text=True)
    else:
        read=lambda p: subprocess.check_output(["git","-C",str(ROOT),"show",f"{surface}:{p}"],text=True)
    return read(README_PATH),read(STATUS_PATH)
def check(surface: str="worktree") -> None: validate_text(*read_authority(surface))
def write() -> None:
    p=ROOT/README_PATH; text=p.read_text(encoding="utf-8"); _,_,rest=text.partition(START); _,_,after=rest.partition(END)
    p.write_text(text.split(START,1)[0]+render_block(canonical_status())+after,encoding="utf-8")
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--check",action="store_true"); parser.add_argument("--write",action="store_true"); parser.add_argument("--surface",choices=("worktree","index"),default="worktree"); args=parser.parse_args()
    if args.write: write()
    else: check(args.surface)
    print("WILSY_PUBLIC_STATUS=PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
