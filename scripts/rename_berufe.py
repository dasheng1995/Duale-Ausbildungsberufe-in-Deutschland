#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 berufe/*.md 重命名为「中文职业名-德语职业名.md」，并更新 README / JSON。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BERUFE_JSON = ROOT / "data" / "berufe.json"
OUT_DIR = ROOT / "berufe"
INDEX_MD = ROOT / "README.md"

INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTI_SPACE = re.compile(r"\s+")
MULTI_DASH = re.compile(r"-{2,}")


def short_de(name: str) -> str:
    return name.split("/")[0].strip()


def safe_part(text: str) -> str:
    """Windows 文件名安全处理，尽量保留可读性。"""
    t = text.strip()
    t = t.replace("/", "／").replace("\\", "＼")
    t = t.replace(":", "：").replace("*", "＊").replace("?", "？")
    t = t.replace('"', "“").replace("<", "＜").replace(">", "＞").replace("|", "｜")
    t = INVALID.sub("", t)
    t = MULTI_SPACE.sub(" ", t).strip(" .")
    return t


def make_filename(zh: str, de: str) -> str:
    return f"{safe_part(zh)}-{safe_part(de)}.md"


def main() -> None:
    dossiers = json.loads(BERUFE_JSON.read_text(encoding="utf-8"))
    used: dict[str, int] = {}
    renames: list[tuple[str, str, dict]] = []  # old_slug, new_filename, dossier

    for d in dossiers:
        zh = d.get("name_zh") or short_de(d["name"])
        de = short_de(d["name"])
        fname = make_filename(zh, de)
        if fname in used:
            used[fname] += 1
            stem = fname[:-3]
            fname = f"{stem}-{used[fname]}.md"
        else:
            used[fname] = 1
        renames.append((d["slug"], fname, d))

    # Two-phase rename to avoid collisions with existing slug names
    tmp_map: dict[str, Path] = {}
    for i, (old_slug, new_fname, d) in enumerate(renames):
        src = OUT_DIR / f"{old_slug}.md"
        if not src.exists():
            # maybe already renamed
            alt = OUT_DIR / new_fname
            if alt.exists():
                tmp_map[old_slug] = alt
                continue
            raise FileNotFoundError(src)
        tmp = OUT_DIR / f"__tmp_rename_{i:04d}.md"
        src.rename(tmp)
        tmp_map[old_slug] = tmp

    slug_to_new: dict[str, str] = {}
    for old_slug, new_fname, d in renames:
        tmp = tmp_map[old_slug]
        dest = OUT_DIR / new_fname
        if dest.exists():
            dest.unlink()
        tmp.rename(dest)
        slug_to_new[old_slug] = new_fname
        d["filename"] = new_fname
        # keep slug for stable id, but record display filename
        # update file 文件名 field inside markdown
        text = dest.read_text(encoding="utf-8")
        text = re.sub(
            r"(\| 文件名 \| `)([^`]+)(` \|)",
            rf"\g<1>{new_fname}\g<3>",
            text,
            count=1,
        )
        dest.write_text(text, encoding="utf-8")

    BERUFE_JSON.write_text(
        json.dumps(dossiers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Update README links: berufe/{slug}.md -> berufe/{new_fname}
    readme = INDEX_MD.read_text(encoding="utf-8")
    for old_slug, new_fname in slug_to_new.items():
        readme = readme.replace(f"berufe/{old_slug}.md", f"berufe/{new_fname}")
    INDEX_MD.write_text(readme, encoding="utf-8")

    print(f"Renamed {len(renames)} files")
    print("Examples:")
    for _, new_fname, _ in renames[:5]:
        print(" ", new_fname)
    print(" ...")
    for _, new_fname, _ in renames[-3:]:
        print(" ", new_fname)


if __name__ == "__main__":
    main()
