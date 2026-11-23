#!/usr/bin/env python3
"""init_project.py — Initialize a new ContentY video/stream production workspace.

Creates local job folders and copies editable templates without overwriting existing work.

Usage:
  python3 scripts/init_project.py my-episode --format faceless --base "$STUDIO_JOBS"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CREATIVE_DIRECTION_TEMPLATE = """# Creative Direction — {title}

- **Format:** {fmt}
- **Tek Cümlelik Vaat:** <!-- İzleyici bu videodan tek cümlede ne alacak? -->
- **Hedef Kitle / Ton:** <!-- Kime konuşuyoruz, neye karşıyız? -->

## Bölüm Eğrisi
| Zaman | Bölüm | Amaç (Hook / Problem / Kanıt / Karşı Tez / Kapanış) | Görsel Rolü | Ses / Müzik |
| :--- | :--- | :--- | :--- | :--- |
| 00:00 | Giriş / Hook | | | |

## Haklar ve Kaynaklar
- B-roll / görsel atıfları `06-metadata/sources.json` içine yazılır.
"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip()).strip("-").lower()
    if not slug:
        raise ValueError(f"Gecersiz proje adi: {name!r}")
    return slug


def copy_if_missing(src: Path, dst: Path, force: bool) -> str:
    if not src.is_file():
        return f"SKIP (missing src): {src}"
    if dst.exists() and not force:
        return f"KEEP: {dst.name}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"COPY: {dst.name}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a ContentY video/stream project")
    parser.add_argument("name", help="Proje adi / slug (orn. yapay-zeka-bolum-01)")
    parser.add_argument(
        "--format",
        choices=["youtube", "faceless", "shorts", "podcast", "stream"],
        default="youtube",
        help="Uretim formati",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=None,
        help="Proje kok dizini (varsayilan: $STUDIO_JOBS veya workspace/projects)",
    )
    parser.add_argument("--force", action="store_true", help="Mevcut sablon dosyalarini ez")
    args = parser.parse_args()

    try:
        slug = slugify(args.name)
    except ValueError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 2

    env_jobs = os.environ.get("STUDIO_JOBS")
    base_dir = args.base or (Path(env_jobs) if env_jobs else REPO_ROOT / "workspace" / "projects")
    job_dir = base_dir / slug

    subdirs = [
        "01-raw",
        "02-cut",
        "03-graphics",
        "04-audio",
        "05-exports",
        "06-metadata",
    ]
    for sub in subdirs:
        (job_dir / sub).mkdir(parents=True, exist_ok=True)

    meta = job_dir / "06-metadata"
    results: list[str] = []

    copies = [
        (REPO_ROOT / "templates" / "edit.json", meta / "edit.json"),
        (REPO_ROOT / "templates" / "kurgu-atolyesi" / "pano-haritasi.md", meta / "pano-haritasi.md"),
        (REPO_ROOT / "templates" / "kurgu-atolyesi" / "marka.md", meta / "marka.md"),
        (REPO_ROOT / "templates" / "kurgu-atolyesi" / "begenmeme-defteri.md", meta / "begenmeme-defteri.md"),
        (REPO_ROOT / "templates" / "video-motoru" / "KURGU-NOTU.md", meta / "KURGU-NOTU.md"),
        (REPO_ROOT / "brand" / "caption-corrections.example.json", meta / "caption-corrections.json"),
        (REPO_ROOT / "brand" / "frame.template.md", meta / "frame.md"),
    ]
    for src, dst in copies:
        results.append(copy_if_missing(src, dst, args.force))

    edit_path = meta / "edit.json"
    if edit_path.is_file():
        try:
            edit_data = json.loads(edit_path.read_text(encoding="utf-8"))
            if edit_data.get("title") == "<Job Title> — edit":
                edit_data["title"] = f"{args.name} — edit"
                edit_path.write_text(json.dumps(edit_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except json.JSONDecodeError:
            pass

    cd_path = meta / "creative_direction.md"
    if not cd_path.exists() or args.force:
        cd_path.write_text(
            CREATIVE_DIRECTION_TEMPLATE.format(title=args.name, fmt=args.format),
            encoding="utf-8",
        )
        results.append("WRITE: creative_direction.md")
    else:
        results.append("KEEP: creative_direction.md")

    src_log = meta / "sources.json"
    if not src_log.exists() or args.force:
        src_log.write_text(json.dumps({"project": slug, "sources": []}, indent=2) + "\n", encoding="utf-8")
        results.append("WRITE: sources.json")

    print(f"Proje hazir: {job_dir} (format={args.format})")
    for line in results:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
