"""Non-destructive checks for case inputs and reference outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CaseConfig


@dataclass(frozen=True)
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"


def validate_case_paths(config: CaseConfig) -> list[ValidationIssue]:
    """Check manifest paths and return issues instead of raising on the first one."""

    issues: list[ValidationIssue] = []
    for key, path in config.paths.items():
        if not path.exists():
            severity = "error" if key.startswith("required_") else "warning"
            issues.append(ValidationIssue(key, f"路径不存在: {path}", severity))
    return issues


def raster_summary(path: Path) -> dict[str, Any]:
    """Read lightweight raster metadata when Rasterio is available."""

    try:
        import rasterio
    except ImportError as exc:
        raise RuntimeError("Rasterio is required for raster inspection") from exc

    with rasterio.open(path) as dataset:
        bounds = dataset.bounds
        return {
            "path": str(path),
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "count": dataset.count,
            "dtype": dataset.dtypes[0],
            "nodata": dataset.nodata,
            "crs": dataset.crs.to_string() if dataset.crs else None,
            "transform": tuple(dataset.transform),
            "bounds": (bounds.left, bounds.bottom, bounds.right, bounds.top),
        }


def vector_summary(path: Path) -> dict[str, Any]:
    """Read lightweight vector metadata when GeoPandas is available."""

    try:
        import geopandas as gpd
    except ImportError as exc:
        raise RuntimeError("GeoPandas is required for vector inspection") from exc

    frame = gpd.read_file(path)
    return {
        "path": str(path),
        "feature_count": len(frame),
        "geometry_type": sorted(frame.geometry.geom_type.dropna().unique().tolist()),
        "crs": frame.crs.to_string() if frame.crs else None,
        "columns": frame.columns.tolist(),
        "bounds": tuple(frame.total_bounds.tolist()) if not frame.empty else None,
    }
