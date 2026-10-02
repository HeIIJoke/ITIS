"""Разрешение путей к статике фронтенда.

Логика вынесена из main.py в чистую функцию без FastAPI: её легко тестировать
(см. tests/test_static_files.py) и переиспользовать.
"""

from pathlib import Path


class StaticFileError(Exception):
    """Запрошенный путь ведёт за пределы папки со статикой (path traversal)."""


def resolve_static_path(frontend_dir: Path, url_path: str) -> Path | None:
    """Находит файл статики по URL-пути.

    Args:
        frontend_dir: корень статики (в проде — папка frontend/).
        url_path: путь из URL без ведущего слеша, например "css/base.css".

    Returns:
        Путь к существующему файлу, либо None — если файла нет и путь похож на
        страницу SPA (без расширения), значит нужно отдать index.html.

    Raises:
        StaticFileError: путь выходит за пределы frontend_dir.
        FileNotFoundError: файл запрошен явно (есть расширение), но его нет.
    """
    root = frontend_dir.resolve()

    if not url_path:
        return root / "index.html"

    candidate = (root / url_path).resolve()

    # "./../../secret.txt" и прочие выходы за корень статики — запрещены.
    if not candidate.is_relative_to(root):
        raise StaticFileError(url_path)

    if candidate.is_file():
        return candidate

    # Путь без расширения — это маршрут SPA ("/teachers" -> index.html).
    if Path(url_path).suffix:
        raise FileNotFoundError(url_path)

    return None
