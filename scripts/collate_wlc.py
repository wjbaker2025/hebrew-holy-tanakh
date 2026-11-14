"""Read-only consonantal collation against a pinned Open Scriptures WLC corpus.

This compares the local 39-book JSON corpus to a separately attributed OSHB
Westminster Leningrad Codex (WLC) XML revision. It does NOT change either text.
Both qere-preferred and ketiv-preferred streams are compared when available.

The OSHB WLC text is public domain; Open Scriptures lemma/morphology data is
CC BY 4.0 and belongs to its credited authors. No upstream files are checked
into the repository as part of this script.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "d4265dfa93b78d82765a557e12d965528c17c1a9"
URL_BASE = ("https://raw.githubusercontent.com/openscriptures/morphhb/"
            + UPSTREAM_COMMIT + "/wlc/")
BOOK_CODES = (
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg",
    "1Sam", "2Sam", "1Kgs", "2Kgs", "Isa", "Jer", "Ezek",
    "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah",
    "Hab", "Zeph", "Hag", "Zech", "Mal", "Ps", "Prov", "Job",
    "Song", "Ruth", "Lam", "Eccl", "Esth", "Dan", "Ezra",
    "Neh", "1Chr", "2Chr",
)
NS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
NUMERIC = re.compile(r"^[1-9]\d*$")


def consonants(text: str) -> str:
    """Read consonantal Hebrew (including final letters), not a translation."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if "\u05d0" <= c <= "\u05ea"
    )


def local_verses(path: Path) -> tuple[dict[tuple[int, int], str], list[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    name = next(iter(doc))
    verses: dict[tuple[int, int], str] = {}
    excluded: list[str] = []
    for chapter, items in doc[name]["chapters"].items():
        for verse, words in items.items():
            if not NUMERIC.fullmatch(chapter) or not NUMERIC.fullmatch(verse):
                excluded.append(f"{name} {chapter}:{verse}")
                continue
            verses[(int(chapter), int(verse))] = consonants(
                "".join(str(word.get("hebrew", "")) for word in words)
            )
    return verses, excluded


def source_verses(xml_bytes: bytes) -> dict[tuple[int, int], tuple[str, str]]:
    root = ET.fromstring(xml_bytes)
    out: dict[tuple[int, int], tuple[str, str]] = {}
    for verse in root.iter(NS + "verse"):
        osis = verse.attrib.get("osisID", "")
        sections = osis.split(".")
        if len(sections) != 3 or not all(NUMERIC.fullmatch(x) for x in sections[1:]):
            continue
        location = (int(sections[1]), int(sections[2]))
        words = list(verse.iter(NS + "w"))
        def stream(excluded_type: str) -> str:
            return consonants("".join(
                "".join(word.itertext()) for word in words
                if word.attrib.get("type") != excluded_type
            ))
        out[location] = (stream("x-ketiv"), stream("x-qere"))
    return out


def missing_description(a: str, b: str) -> list[dict[str, str]]:
    """Return the first few exact differing Hebrew consonant spans."""
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out: list[dict[str, str]] = []
    for opcode, i, j, k, n in sm.get_opcodes():
        if opcode == "equal":
            continue
        out.append({"operation": opcode, "local": a[i:j][:80], "upstream": b[k:n][:80]})
        if len(out) == 4:
            break
    return out


def obtain_xml(code: str, source_dir: Path | None) -> bytes:
    if source_dir is not None:
        return (source_dir / f"{code}.xml").read_bytes()
    req = urllib.request.Request(
        URL_BASE + f"{code}.xml", headers={"User-Agent": "HebrewHolyTanakh-WLC-collation/1.0"}
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def collate(source_dir: Path | None = None, max_examples: int = 80) -> dict:
    json_files = {
        int(f.name[:2]): f for f in (ROOT / "Tanakh").rglob("*.json")
        if re.fullmatch(r"[0-9]{2}_.+[.]json", f.name)
    }
    if sorted(json_files) != list(range(1, 40)):
        raise ValueError("Expected all 39 numbered Tanakh books")
    summary = Counter()
    per_book: list[dict] = []
    difference_categories = Counter()
    examples: list[dict] = []
    excluded: list[str] = []
    errors: list[str] = []
    for number, code in enumerate(BOOK_CODES, start=1):
        local, nonnumeric = local_verses(json_files[number])
        excluded.extend(nonnumeric)
        counts = Counter()
        try:
            upstream = source_verses(obtain_xml(code, source_dir))
        except (OSError, ValueError, ET.ParseError) as exc:
            errors.append(f"{code}: {exc}")
            continue
        for ref in sorted(set(local) | set(upstream)):
            present_local = local.get(ref)
            present_upstream = upstream.get(ref)
            location = f"{code} {ref[0]}:{ref[1]}"
            if present_local is None:
                counts["missing_local_verses"] += 1
                if len(examples) < max_examples:
                    examples.append({"ref": location, "issue": "missing local verse"})
            elif present_upstream is None:
                counts["extra_local_verses"] += 1
                if len(examples) < max_examples:
                    examples.append({"ref": location, "issue": "extra local verse"})
            elif present_local == present_upstream[0]:
                counts["match_qere_preferred"] += 1
            elif present_local == present_upstream[1]:
                counts["match_ketiv_preferred"] += 1
            else:
                counts["different_consonants"] += 1
                operations = {
                    opcode
                    for opcode, _, _, _, _ in difflib.SequenceMatcher(
                        a=present_local, b=present_upstream[0], autojunk=False
                    ).get_opcodes()
                    if opcode != "equal"
                }
                if operations == {"insert"}:
                    difference_categories["local_omissions_only"] += 1
                elif operations == {"delete"}:
                    difference_categories["local_additions_only"] += 1
                else:
                    difference_categories["mixed_or_replacements"] += 1
                if len(examples) < max_examples:
                    examples.append({
                        "ref": location,
                        "issue": "consonants differ",
                        "local": present_local[:220],
                        "upstream_qere_preferred": present_upstream[0][:220],
                        "diff": missing_description(present_local, present_upstream[0]),
                    })
        summary.update(counts)
        per_book.append({"book": code, **counts})
    return {
        "source": "Open Scriptures Hebrew Bible, WLC digital transcription",
        "source_commit": UPSTREAM_COMMIT,
        "source_url": URL_BASE,
        "source_license": "WLC text public domain; morphology CC BY 4.0",
        "status": "complete" if not errors else "incomplete",
        "books_collated": len(per_book),
        "summary": dict(summary),
        "difference_categories": dict(difference_categories),
        "excluded_nonnumeric_local_refs": excluded,
        "errors": errors,
        "examples": examples,
        "per_book": per_book,
        "interpretation": (
            "A difference is an editorial/transcription/segmentation signal, not "
            "automatically an ancient manuscript variant or a justified correction. "
            "This comparison checks consonant streams, NOT niqqud, accents, "
            "morpheme divisions, Strong's IDs or English glosses."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Local directory of pinned OSHB WLC XML")
    parser.add_argument("--output", type=Path, default=Path("wlc-collation.json"))
    parser.add_argument("--examples", type=int, default=80,
                        help="Maximum example records; use 10000 to retain all verse-level differences")
    args = parser.parse_args()
    result = collate(args.source_dir, args.examples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "books": result["books_collated"],
        "summary": result["summary"], "difference_categories": result["difference_categories"],
        "errors": result["errors"]
    }, ensure_ascii=False))
    if result["status"] != "complete":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
