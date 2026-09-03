from pathlib import Path

from basin_tool.config import CaseConfig
from basin_tool.validation import validate_case_paths


def test_required_and_optional_missing_paths_have_different_severity(tmp_path):
    config = CaseConfig(
        manifest_path=tmp_path / "case.json",
        project_root=tmp_path,
        name="test",
        description="",
        paths={
            "required_dem": tmp_path / "missing.tif",
            "reference_stream": tmp_path / "missing.shp",
        },
        processing={"flow_accumulation_threshold": 10},
        arcgis={},
    )

    issues = validate_case_paths(config)

    assert [(issue.key, issue.severity) for issue in issues] == [
        ("required_dem", "error"),
        ("reference_stream", "warning"),
    ]
