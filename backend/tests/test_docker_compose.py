from pathlib import Path


def test_docker_compose_declares_full_stack():
    compose_path = Path(__file__).resolve().parents[2] / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")

    assert "mysql:" in content
    assert "backend:" in content
    assert "frontend:" in content
    assert "8000:8000" in content
    assert "3000:3000" in content


def test_backend_and_frontend_dockerfiles_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / "backend" / "Dockerfile").is_file()
    assert (root / "frontend" / "Dockerfile").is_file()
