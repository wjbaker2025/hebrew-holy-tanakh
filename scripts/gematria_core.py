"""Reproducible letter-value scoring with script-specific Unicode normalization.

Numbers come from gemantria/mappings/gemantria_ciphers.json, never from
translated English glosses or transliterated Hebrew-to-Greek placeholders.
This module makes no assertion that experimental mappings are ancient.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
MAPPING_FILE = ROOT / "gemantria" / "mappings" / "gemantria_ciphers.json"
HEBREW_FINALS = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})
SUPPORTED_SCRIPTS = {"hebrew", "greek", "syriac"}


def load_ciphers(path: Path = MAPPING_FILE) -> dict[str, dict[str, int]]:
    """Load the project's canonical letter-value tables, excluding metadata."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        name: entry["mapping"]
        for name, entry in raw["ciphers"].items()
        if isinstance(entry, dict) and isinstance(entry.get("mapping"), dict)
    }


def normalize_letters(text: str, script: str) -> str:
    """Strip vowel/chant accents and canonicalize positional letter forms."""
    if script not in SUPPORTED_SCRIPTS:
        raise ValueError(f"Unsupported script: {script}")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    decomposed = unicodedata.normalize("NFKD", text)
    letters = "".join(
        char for char in decomposed if not unicodedata.category(char).startswith("M")
    )
    if script == "hebrew":
        return letters.translate(HEBREW_FINALS)
    if script == "greek":
        # NFKD plus lower() also normalizes accented polytonic Greek letters.
        return letters.lower().replace("ς", "σ").replace("ϲ", "σ")
    return letters


def score_text(text: str, cipher: str, script: str,
               tables: Mapping[str, Mapping[str, int]] | None = None) -> int:
    """Compute an integer sum; reject unrecognized letters instead of omitting.

    Non-letter characters (spacing, numbers and punctuation) are ignored.
    Script selection is explicit to prevent cross-language silent zero scores.
    """
    if tables is None:
        tables = load_ciphers()
    if cipher not in tables:
        raise ValueError(f"Unknown cipher: {cipher}")
    value_map = tables[cipher]
    total = 0
    for char in normalize_letters(text, script):
        if char in value_map:
            total += value_map[char]
        elif unicodedata.category(char).startswith("L"):
            raise ValueError(f"Letter {char!r} is not defined in {cipher}/{script}")
    return total
