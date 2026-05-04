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


def main() -> None:
    ATMX_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    items = [_build_item(path) for path in sorted(ATMX_DIR.glob("*.atmx"))]
    items.sort(key=lambda item: (str(item.get("course_name") or ""), str(item.get("package_filename") or "")))
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
