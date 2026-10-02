"""Тесты раздачи статики: поиск файла, SPA-fallback, защита от path traversal.

FastAPI здесь не нужен — это чистая функция, поэтому тесты мгновенные.
"""

from pathlib import Path

import pytest

from api.app.core.static_files import StaticFileError, resolve_static_path


@pytest.fixture(scope="module")
def frontend_dir() -> Path:
    """Настоящая папка фронтенда — тестируем на реальных файлах."""
    return Path(__file__).resolve().parents[1] / "frontend"


def test_root_returns_index_html(frontend_dir: Path) -> None:
    result = resolve_static_path(frontend_dir, "")

    assert result is not None
    assert result.name == "index.html"
    assert result.is_file()


def test_existing_asset_is_found(frontend_dir: Path) -> None:
    result = resolve_static_path(frontend_dir, "css/base.css")

    assert result is not None
    assert result.is_file()
    assert result.suffix == ".css"


def test_page_without_extension_falls_back_to_spa(frontend_dir: Path) -> None:
    assert resolve_static_path(frontend_dir, "teachers") is None


def test_missing_file_with_extension_raises(frontend_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_static_path(frontend_dir, "css/no-such-file.css")


@pytest.mark.parametrize(
    "attack",
    [
        "../api/app/main.py",
        "../../etc/passwd",
        "css/../../README.md",
    ],
)
def test_path_traversal_is_blocked(frontend_dir: Path, attack: str) -> None:
    with pytest.raises(StaticFileError):
        resolve_static_path(frontend_dir, attack)
