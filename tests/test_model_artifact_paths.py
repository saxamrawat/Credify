from __future__ import annotations

from pathlib import Path

from propensity_prediction.models.artifact import (
    MODEL_ARTIFACT_RELATIVE_PATH,
    _default_model_artifact_path,
)


def test_artifact_path_can_be_configured_with_environment(
    monkeypatch, tmp_path: Path
) -> None:
    configured_path = tmp_path / "custom" / "risk-model.joblib"
    monkeypatch.setenv("PROPENSITY_MODEL_ARTIFACT_PATH", str(configured_path))

    assert _default_model_artifact_path() == configured_path


def test_regular_package_install_can_find_artifact_from_working_directory(
    monkeypatch, tmp_path: Path
) -> None:
    model_path = tmp_path / MODEL_ARTIFACT_RELATIVE_PATH
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"test bundle placeholder")
    monkeypatch.delenv("PROPENSITY_MODEL_ARTIFACT_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    assert _default_model_artifact_path() == model_path
