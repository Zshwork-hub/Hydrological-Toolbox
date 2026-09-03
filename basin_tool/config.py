"""Project and benchmark configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a case manifest is invalid."""


@dataclass(frozen=True)
class CaseConfig:
    """A resolved case manifest with paths relative to the project root."""

    manifest_path: Path
    project_root: Path
    name: str
    description: str
    paths: dict[str, Path]
    processing: dict[str, Any]
    arcgis: dict[str, Any]

    @property
    def threshold(self) -> float:
        return float(self.processing["flow_accumulation_threshold"])

    def required_paths(self) -> dict[str, Path]:
        return {
            key: value
            for key, value in self.paths.items()
            if key.startswith("required_")
        }


def _resolve_path(value: str, project_root: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (project_root / path).resolve()


def load_case_manifest(
    manifest_path: str | Path,
    *,
    project_root: str | Path | None = None,
) -> CaseConfig:
    """Load and resolve a JSON case manifest without touching source data."""

    manifest = Path(manifest_path).expanduser().resolve()
    if not manifest.is_file():
        raise ConfigError(f"Manifest does not exist: {manifest}")

    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in manifest: {manifest}") from exc

    if project_root is None:
        project_root = manifest.parents[1] if manifest.parent.name == "benchmarks" else manifest.parent
    root = Path(project_root).expanduser().resolve()

    if not isinstance(payload, dict):
        raise ConfigError("Manifest root must be an object")

    for key in ("name", "paths", "processing", "arcgis"):
        if key not in payload:
            raise ConfigError(f"Manifest is missing required key: {key}")

    if not isinstance(payload["paths"], dict):
        raise ConfigError("Manifest key 'paths' must be an object")
    if not isinstance(payload["processing"], dict):
        raise ConfigError("Manifest key 'processing' must be an object")
    if not isinstance(payload["arcgis"], dict):
        raise ConfigError("Manifest key 'arcgis' must be an object")

    invalid_paths = [
        key for key, value in payload["paths"].items() if not isinstance(value, str)
    ]
    if invalid_paths:
        raise ConfigError(f"Manifest paths must be strings: {', '.join(invalid_paths)}")

    paths = {
        key: _resolve_path(value, root)
        for key, value in payload["paths"].items()
    }
    processing = payload["processing"]
    threshold = processing.get("flow_accumulation_threshold")
    if isinstance(threshold, bool):
        raise ConfigError("flow_accumulation_threshold must be a finite number")
    try:
        threshold_value = float(threshold)
    except (TypeError, ValueError) as exc:
        raise ConfigError("flow_accumulation_threshold must be a finite number") from exc
    if not math.isfinite(threshold_value) or threshold_value <= 0:
        raise ConfigError("flow_accumulation_threshold must be greater than zero")

    return CaseConfig(
        manifest_path=manifest,
        project_root=root,
        name=str(payload["name"]),
        description=str(payload.get("description", "")),
        paths=paths,
        processing=dict(processing),
        arcgis=dict(payload["arcgis"]),
    )
