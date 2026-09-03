"""Command-line entry points used during development and validation."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .config import ConfigError, load_case_manifest
from .validation import raster_summary, validate_case_paths, vector_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="basin-tool")
    commands = parser.add_subparsers(dest="command", required=True)

    for name in ("validate-case", "inspect-case"):
        command = commands.add_parser(name, help=f"{name.replace('-', ' ')}")
        command.add_argument("manifest", help="Path to a JSON case manifest")
        command.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def _print(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2, default=str))
    elif isinstance(value, list):
        for item in value:
            print(item)
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        config = load_case_manifest(args.manifest)
    except ConfigError as exc:
        print(f"配置错误: {exc}")
        return 2

    if args.command == "validate-case":
        issues = validate_case_paths(config)
        result = [issue.__dict__ for issue in issues]
        if not issues:
            result = [{"severity": "ok", "message": "所有案例路径均存在"}]
        _print(result, args.json)
        return 1 if any(issue.severity == "error" for issue in issues) else 0

    summaries: dict[str, Any] = {
        "name": config.name,
        "description": config.description,
        "threshold": config.threshold,
        "paths": {key: str(path) for key, path in config.paths.items()},
        "processing": config.processing,
        "arcgis": config.arcgis,
    }
    for key, path in config.paths.items():
        if not path.exists():
            continue
        try:
            if path.suffix.lower() in {".tif", ".img"} or (
                path.is_dir() and (path / "hdr.adf").is_file()
            ):
                summaries.setdefault("raster", {})[key] = raster_summary(path)
            elif path.is_dir():
                summaries.setdefault("inspection_warnings", {})[key] = (
                    "目录不是可识别的 Arc/Info GRID，已跳过栅格摘要"
                )
            elif path.suffix.lower() == ".shp":
                summaries.setdefault("vector", {})[key] = vector_summary(path)
        except Exception as exc:
            summaries.setdefault("inspection_warnings", {})[key] = str(exc)
    _print(summaries, args.json)
    return 0
