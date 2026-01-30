from __future__ import annotations

import json
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_books(doc: Dict[str, Any]) -> List[str]:
    return list(doc.keys())


def _sorted_key(x: str):
    try:
        return int(x)
    except Exception:
        return x


def flatten_tokens(doc: Dict[str, Any], book: str, chapter: str) -> List[dict]:
    """
    Returns tokens in the order stored in the JSON (which in your sample is already reading order).
    Each token includes ref / hebrew / strongs / morphology / english.
    """
    if book not in doc:
        raise KeyError(f"Book '{book}' not found. Available: {list(doc.keys())}")

    chapters = doc[book].get("chapters", {})
    if chapter not in chapters:
        raise KeyError(f"Chapter '{chapter}' not found in {book}. Available: {list(chapters.keys())[:20]}...")

    ch = chapters[chapter]
    out: List[dict] = []

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
