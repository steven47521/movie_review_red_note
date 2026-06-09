from pathlib import Path


def test_render_blueprint_exists():
    root = Path(__file__).resolve().parents[2]
    content = (root / "render.yaml").read_text(encoding="utf-8")
    assert "rednote-api" in content
    assert "rednote-web" in content
    assert "healthCheckPath: /health" in content


def test_railway_config_exists():
    root = Path(__file__).resolve().parents[2]
    assert (root / "railway.toml").is_file()


def test_deployment_doc_exists():
    root = Path(__file__).resolve().parents[2]
    doc = (root / "docs" / "DEPLOYMENT.md").read_text(encoding="utf-8")
    assert "Render" in doc
    assert "Railway" in doc
    assert "NEXT_PUBLIC_API_URL" in doc
    assert "CORS_ORIGINS" in doc
