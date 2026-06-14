from __future__ import annotations

import json
from typing import Any


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_books(doc: dict[str, Any]) -> list[str]:
    return list(doc.keys())


def _sorted_key(x: str) -> tuple[int, int | str]:
    try:
        return (0, int(x))
    except Exception:
        return (1, x)


def flatten_tokens(doc: dict[str, Any], book: str, chapter: str) -> list[dict]:
    """Return tokens in a stable reading order (verses sorted numerically when possible).

    Each token includes ref / hebrew / strongs / morphology / english.
    """
    if book not in doc:
        raise KeyError(f"Book '{book}' not found. Available: {list(doc.keys())}")

    chapters = doc[book].get("chapters", {})
    if chapter not in chapters:
        raise KeyError(f"Chapter '{chapter}' not found in {book}. Available: {list(chapters.keys())[:20]}...")

    ch = chapters[chapter]
    out: list[dict] = []

    for verse_num in sorted(ch.keys(), key=_sorted_key):
        verse = ch[verse_num]
        for tok in verse:
            out.append({
                "ref": f"{book} {chapter}:{verse_num}",
                "hebrew": tok.get("hebrew", ""),
                "english": tok.get("english", ""),
                "strongs": tok.get("strongs", ""),
                "morphology": tok.get("morphology", ""),
            })
    return out
