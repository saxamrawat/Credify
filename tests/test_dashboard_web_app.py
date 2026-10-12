from __future__ import annotations

from propensity_prediction.api.routes import dashboard_config
from propensity_prediction.data.schema import get_feature_columns
from propensity_prediction.dashboard import STATIC_ASSETS_DIRECTORY


def test_dashboard_config_uses_api_schema_and_row_limit() -> None:
    config = dashboard_config()

    assert config.max_customer_rows == 30_000
    assert config.required_columns[0] == "ID"
    assert len(config.required_columns) == 24
    assert config.required_columns[1:] == get_feature_columns()


def test_custom_dashboard_static_assets_are_packaged() -> None:
    page = (STATIC_ASSETS_DIRECTORY / "index.html").read_text()
    styles = (STATIC_ASSETS_DIRECTORY / "styles.css").read_text()
    script = (STATIC_ASSETS_DIRECTORY / "app.js").read_text()

    assert "Portfolio overview" in page
    assert "--canvas" in styles
    assert "validateCsvRows" in script
    assert "customer-explanation" in script
    assert "Download filtered CSV" in page
    assert 'new Set(["SEX", "EDUCATION", "MARRIAGE"])' in script
    assert '"Historical outcome fields included", "No"' in script
