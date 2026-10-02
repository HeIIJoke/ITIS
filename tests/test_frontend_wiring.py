"""Проверка связки фронтенда: пути к статике, страницы и обработчики SPA.

Эти тесты работают с файлами напрямую (без HTTP и без запуска сервера) —
они быстро ловят опечатки в путях, которые иначе видны только в браузере.
"""

import re
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _index_asset_refs() -> list[str]:
    """Локальные src/href из index.html без SPA-ссылок (у них есть data-link)."""
    refs = []
    for tag in re.findall(r"<[^>]+>", _read(FRONTEND / "index.html")):
        if "data-link" in tag:
            continue  # это маршрут SPA, а не файл на диске
        refs.extend(re.findall(r'(?:href|src)="(/[^"]+)"', tag))
    return refs


def test_index_assets_exist() -> None:
    refs = _index_asset_refs()

    assert refs, "в index.html не найдено ни одной ссылки на статику"
    for ref in refs:
        assert (FRONTEND / ref.lstrip("/")).is_file(), f"нет файла: {ref}"


def test_router_pages_exist() -> None:
    router = _read(FRONTEND / "js" / "router.js")
    pages = re.findall(r'file:\s*"([^"]+)"', router)

    assert pages, "в router.js не найдено ни одной страницы"
    for page in pages:
        assert (FRONTEND / page.lstrip("/")).is_file(), f"нет страницы: {page}"


def test_router_nav_links_exist() -> None:
    """У каждого маршрута (кроме «/») должна быть ссылка в навигации."""
    router = _read(FRONTEND / "js" / "router.js")
    index = _read(FRONTEND / "index.html")

    for route in re.findall(r'^\s*"([^"]+)":\s*\{', router, re.MULTILINE):
        if route == "/":
            continue
        assert f'href="{route}"' in index, f"нет ссылки навигации для {route}"


def test_router_handlers_are_defined() -> None:
    """Функции init<Страница> должны быть реально объявлены в JS."""
    router = _read(FRONTEND / "js" / "router.js")
    sources = "\n".join(
        path.read_text(encoding="utf-8") for path in (FRONTEND / "js").rglob("*.js")
    )

    handlers = re.findall(r"init:\s*\(\)\s*=>\s*(\w+)\(\)", router)
    assert handlers, "в router.js не найдено ни одного init-обработчика"
    for handler in handlers:
        assert re.search(
            rf"function\s+{handler}\s*\(", sources
        ), f"функция {handler} не объявлена ни в одном js-файле"


def test_page_markup_has_elements_used_by_script() -> None:
    """id, которые ищет страница через getElementById, должны быть в разметке."""
    page_markup = _read(FRONTEND / "pages" / "home.html")
    page_script = _read(FRONTEND / "js" / "pages" / "home.js")

    for element_id in re.findall(r'getElementById\("([^"]+)"\)', page_script):
        assert f'id="{element_id}"' in page_markup, f"нет элемента #{element_id}"
