from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ATMX_DIR = ROOT / "demo-courses" / "atmx"
CATALOG_PATH = ROOT / "demo-courses" / "catalog" / "v1" / "index.json"
DISPLAY_ORDER_PATH = ROOT / "demo-courses" / "catalog" / "v1" / "display-order.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip()).strip("-._")
    return slug or "demo-course"


def _read_manifest(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as package:
        try:
            with package.open("manifest.json") as manifest_file:
                return json.loads(manifest_file.read().decode("utf-8"))
        except KeyError as exc:
            raise ValueError(f"{path}: missing manifest.json") from exc


def _build_item(path: Path) -> dict[str, Any]:
    manifest = _read_manifest(path)
    course = manifest.get("course") if isinstance(manifest.get("course"), dict) else {}
    stats = manifest.get("stats") if isinstance(manifest.get("stats"), dict) else {}

    course_name = str(course.get("name") or path.stem).strip()
    course_id = str(course.get("course_id") or path.stem).strip()
    package_ref = quote(path.relative_to(ROOT / "demo-courses").as_posix(), safe="/._-")

    return {
        "id": _slugify(course_id or path.stem),
        "course_id": course_id,
        "course_name": course_name,
        "package_url": package_ref,
        "package_filename": path.name,
        "file_size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "exported_at": manifest.get("exported_at"),
        "stats": stats,
        "description": course.get("description") or "",
        "icon_key": course.get("icon_key"),
    }


def _read_display_order() -> list[str]:
    if not DISPLAY_ORDER_PATH.exists():
        return []

    payload = json.loads(DISPLAY_ORDER_PATH.read_text(encoding="utf-8"))
    packages = payload.get("packages") if isinstance(payload, dict) else None
    if not isinstance(packages, list):
        raise ValueError(f"{DISPLAY_ORDER_PATH}: packages must be a list")

    ordered_packages: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(packages, start=1):
        package_filename = str(value or "").strip()
        if not package_filename:
            raise ValueError(f"{DISPLAY_ORDER_PATH}: packages[{index}] must be a non-empty filename")
        if package_filename in seen:
            raise ValueError(f"{DISPLAY_ORDER_PATH}: duplicate package filename: {package_filename}")
        seen.add(package_filename)
        ordered_packages.append(package_filename)
    return ordered_packages


def _sort_items_for_display(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered_packages = _read_display_order()
    rank_by_filename = {filename: index for index, filename in enumerate(ordered_packages)}
    available_filenames = {str(item.get("package_filename") or "") for item in items}
    missing_filenames = [filename for filename in ordered_packages if filename not in available_filenames]
    if missing_filenames:
        missing = ", ".join(missing_filenames)
        raise ValueError(f"{DISPLAY_ORDER_PATH}: package files not found: {missing}")

    def display_key(item: dict[str, Any]) -> tuple[int, int, str, str]:
        filename = str(item.get("package_filename") or "")
        if filename in rank_by_filename:
            return (0, rank_by_filename[filename], "", filename)
        course_name = str(item.get("course_name") or "")
        return (1, 0, course_name.casefold(), filename.casefold())

    return sorted(items, key=display_key)


def main() -> None:
    ATMX_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    items = [_build_item(path) for path in sorted(ATMX_DIR.glob("*.atmx"))]
    items = _sort_items_for_display(items)
    existing_payload = _read_existing_catalog()
    generated_at = (
        existing_payload.get("generated_at")
        if existing_payload.get("courses") == items
        else _utc_now_iso()
    )

    payload = {
        "schema": "aiteachme.demo_courses.catalog.v1",
        "generated_at": generated_at,
        "courses": items,
    }
    CATALOG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_existing_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {}
    try:
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


if __name__ == "__main__":
    main()
