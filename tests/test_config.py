import json

import pytest

from basin_tool.config import ConfigError, load_case_manifest


def test_load_case_manifest_resolves_paths(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "dem.tif").touch()
    manifest = tmp_path / "case.json"
    manifest.write_text(
        json.dumps(
            {
                "name": "test",
                "paths": {"required_dem": "data/dem.tif"},
                "processing": {"flow_accumulation_threshold": 10},
                "arcgis": {"version": "Desktop 10.8.2"},
            }
        ),
        encoding="utf-8",
    )

    config = load_case_manifest(manifest, project_root=tmp_path)

    assert config.name == "test"
    assert config.threshold == 10
    assert config.paths["required_dem"] == (tmp_path / "data" / "dem.tif").resolve()


def test_invalid_threshold_is_rejected(tmp_path):
    manifest = tmp_path / "case.json"
    manifest.write_text(
        json.dumps(
            {
                "name": "test",
                "paths": {},
                "processing": {"flow_accumulation_threshold": 0},
                "arcgis": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="greater than zero"):
        load_case_manifest(manifest, project_root=tmp_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("paths", [], "must be an object"),
        ("processing", [], "must be an object"),
        ("arcgis", [], "must be an object"),
        ("paths", {"required_dem": 1}, "paths must be strings"),
        ("processing", {"flow_accumulation_threshold": "bad"}, "finite number"),
        ("processing", {"flow_accumulation_threshold": "NaN"}, "greater than zero"),
    ],
)
def test_malformed_manifest_is_reported_as_config_error(tmp_path, field, value, message):
    payload = {
        "name": "test",
        "paths": {},
        "processing": {"flow_accumulation_threshold": 10},
        "arcgis": {},
    }
    payload[field] = value
    manifest = tmp_path / "case.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_case_manifest(manifest, project_root=tmp_path)


def test_non_object_manifest_is_reported_as_config_error(tmp_path):
    manifest = tmp_path / "case.json"
    manifest.write_text("[]", encoding="utf-8")

    with pytest.raises(ConfigError, match="root must be an object"):
        load_case_manifest(manifest, project_root=tmp_path)
