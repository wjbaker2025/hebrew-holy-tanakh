"""Read-only repository-wide structural and numerical integrity audit.

Usage:
    python -m scripts.audit_repository --deep --output audit-report.json

What this can establish: file integrity, parseability, metadata consistency,
book/verse/token schema, and tracked asset readability.
What this CANNOT establish: agreement with every word of an external WLC,
an autograph, the antiquity of a proposed gematria cipher, or the accuracy
of English glosses. Those require a separately identified textual witness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HEBREW_VALUES = dict(zip("אבגדהוזחטיכלמנסעפצקרשת",
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                          20, 30, 40, 50, 60, 70, 80, 90, 100,
                          200, 300, 400]))
NUMBERED_BOOK = re.compile(r"^(\d{2})_.+\.json$")
REF_NUMERIC = re.compile(r"^[1-9]\d*$")


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, Any] = {}
        self.warning_counts: dict[str, int] = {}

    def error(self, message: str) -> None:
        # Keep every structural error bounded to avoid multi-megabyte output.
        if len(self.errors) < 80:
            self.errors.append(message)

    def warn(self, code: str, message: str) -> None:
        self.warning_counts[code] = self.warning_counts.get(code, 0) + 1
        if len(self.warnings) < 80:
            self.warnings.append(f"{code}: {message}")

    def report(self) -> dict[str, Any]:
        return {
            "status": "pass" if not self.errors else "fail",
            "stats": self.stats,
            "error_count_sampled": len(self.errors),
            "errors": self.errors,
            "warning_counts": self.warning_counts,
            "warning_examples": self.warnings,
            "limits": [
                "A parseable local corpus does not guarantee fidelity to Leningrad B19a.",
                "No external manuscript text is automatically substituted or rewritten.",
                "Proposed numerical models are not labeled historically proven.",
                "Translation and morphological glosses require separate scholarly collation.",
            ],
        }


def read_json(path: Path, audit: Audit) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        audit.error(f"{path.relative_to(ROOT)}: unreadable JSON: {exc}")
        return None


def audit_corpus(audit: Audit) -> None:
    files = sorted(
        (p for p in (ROOT / "Tanakh").rglob("*.json")
         if NUMBERED_BOOK.fullmatch(p.name)),
        key=lambda p: int(p.name.split("_", 1)[0]),
    )
    found_ids = [int(p.name.split("_", 1)[0]) for p in files]
    if found_ids != list(range(1, 40)):
        audit.error(f"Expected exactly 39 book numbers 01-39, found {found_ids}")

    books: set[str] = set()
    stats = {
        "book_files": len(files), "chapter_rows": 0,
        "verse_rows": 0, "token_rows": 0,
        "missing_numeric_greek_renderings": 0,
        "non_numeric_chapter_or_verse_keys": 0,
        "empty_hebrew_tokens": 0,
        "non_numeric_strongs_tokens": 0,
    }
    digest = hashlib.sha256()
    for path in files:
        # Whole-source fingerprints include original bytes, rather than normalized
        # wording; never mutate source text just to make a checksum match.
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        doc = read_json(path, audit)
        if not isinstance(doc, dict) or len(doc) != 1:
            audit.error(f"{path.relative_to(ROOT)}: expected one book root")
            continue
        book, metadata = next(iter(doc.items()))
        if book in books:
            audit.error(f"Duplicate book identifier: {book}")
        books.add(book)
        if not isinstance(metadata, dict):
            audit.error(f"{book}: book metadata must be an object")
            continue
        chapters = metadata.get("chapters")
        if not isinstance(chapters, dict) or not chapters:
            audit.error(f"{book}: missing chapter map")
            continue
        stats["chapter_rows"] += len(chapters)
        for cnum, verses in chapters.items():
            if not REF_NUMERIC.fullmatch(str(cnum)):
                stats["non_numeric_chapter_or_verse_keys"] += 1
                audit.warn("chapter_key", f"{book} chapter key {cnum!r}")
            if not isinstance(verses, dict) or not verses:
                audit.error(f"{book} {cnum}: missing verse map")
                continue
            stats["verse_rows"] += len(verses)
            verse_numbers = [int(v) for v in verses if REF_NUMERIC.fullmatch(str(v))]
            if len(verse_numbers) == len(verses) and sorted(verse_numbers) != list(
                range(1, len(verses) + 1)
            ):
                audit.warn("verse_numbering", f"{book} {cnum}: nonsequential verses")
            for vnum, tokens in verses.items():
                if not REF_NUMERIC.fullmatch(str(vnum)):
                    stats["non_numeric_chapter_or_verse_keys"] += 1
                    audit.warn("verse_key", f"{book} {cnum}:{vnum} has nonnumeric key")
                if not isinstance(tokens, list) or not tokens:
                    audit.error(f"{book} {cnum}:{vnum}: missing token array")
                    continue
                stats["token_rows"] += len(tokens)
                for index, token in enumerate(tokens):
                    location = f"{book} {cnum}:{vnum} word {index + 1}"
                    if not isinstance(token, dict):
                        audit.error(f"{location}: expected word object")
                        continue
                    hebrew = token.get("hebrew")
                    if not isinstance(hebrew, str) or not hebrew.strip():
                        stats["empty_hebrew_tokens"] += 1
                        audit.error(f"{location}: empty Hebrew token")
                    if "hebrew_greek" not in token:
                        stats["missing_numeric_greek_renderings"] += 1
                    if not isinstance(token.get("strongs", ""), str):
                        audit.warn("strongs_type", f"{location}: Strong's must be a string")
                    elif token.get("strongs") and not str(token["strongs"]).isdigit():
                        stats["non_numeric_strongs_tokens"] += 1
                    if not isinstance(token.get("morphology", ""), str):
                        audit.warn("morphology_type", f"{location}: morphology not string")
    stats["source_files_sha256"] = digest.hexdigest()
    audit.stats["corpus"] = stats
    if stats["missing_numeric_greek_renderings"]:
        audit.warn("rendering_missing", f"{stats['missing_numeric_greek_renderings']} word objects have no numeric Greek rendering")
    if stats["non_numeric_strongs_tokens"]:
        audit.warn("strongs_non_numeric", f"{stats['non_numeric_strongs_tokens']} nonnumeric Strong's codes require review")


def audit_mappings(audit: Audit) -> None:
    folder = ROOT / "gemantria" / "mappings"
    files = sorted(folder.glob("*.json"))
    for path in files:
        read_json(path, audit)
    path = folder / "gemantria_ciphers.json"
    data = read_json(path, audit)
    if not isinstance(data, dict):
        return
    ciphers = data.get("ciphers", {})
    if ciphers.get("standard", {}).get("mapping") != HEBREW_VALUES:
        audit.error("Standard Hebrew gematria values differ from documented Mispar Hechrechi")
    for name in ("biblical", "reversal", "genesis_order", "standard",
                 "greek_transposition", "greek_isopsephy", "syriac_standard"):
        if name not in ciphers or "mapping" not in ciphers[name] and "values" not in ciphers[name]:
            audit.error(f"Missing cipher table: {name}")
    greek_tr = ciphers.get("greek_transposition", {}).get("mapping", {})
    greek_hist = ciphers.get("greek_isopsephy", {}).get("mapping", {})
    if any(greek_tr.get(ch) != 200 for ch in ("σ", "ς", "ϲ")):
        audit.error("Experimental Greek transposition omits or mis-scores a sigma form")
    if any(greek_hist.get(ch) != 200 for ch in ("σ", "ς", "ϲ")):
        audit.error("Conventional Greek isopsephy omits or mis-scores a sigma form")
    if greek_hist.get("ϡ") != 900:
        audit.error("Traditional Greek sampi must equal 900")
    if len(ciphers.get("syriac_standard", {}).get("mapping", {})) != 22:
        audit.error("Syriac numeral table must contain 22 letter values")
    for entry in data.get("languages", {}).get("hebrew", []):
        k = entry["letter"]
        for src, field in (("biblical", "biblical"), ("reversal", "reversal"),
                           ("genesis_order", "genesis"), ("standard", "standard")):
            expected = ciphers[src].get("mapping", ciphers[src].get("values", {})).get(k)
            if expected != entry["values"][field]:
                audit.error(f"Hebrew duplicated metadata mismatch {k} {src}")
    greek_by_letter = {x["letter"]: x for x in data.get("languages", {}).get("greek", [])}
    for entry in ciphers.get("greek_letters", []):
        k = entry["greek_letter"]
        mirror = greek_by_letter.get(k, {}).get("values", {})
        for field, primary in (("biblical_gematria", "biblical"),
                               ("reversal_cipher", "reversal"),
                               ("standard_greek_gematria", "standard")):
            if entry[field] != mirror.get(primary):
                audit.error(f"Greek duplicate mismatch {k} {field}")
    other = read_json(folder / "gematria_multiscript_map.json", audit)
    if isinstance(other, dict):
        cross = other.get("gematria_multiscript_map", {})
        for item in cross.get("mappings", []):
            for char in item.get("greek_letters", []):
                if char.get("letter") == "β" and char.get("reversal_cipher") != 200:
                    audit.error("Multiscript Beta reversal conflicts with canonical mapping")
        if cross.get("language_chars", {}).get("syriac") is None:
            audit.error("Multiscript Syriac numeric values missing")
    audit.stats["mapping_json_files"] = len(files)


def audit_assets(audit: Audit, deep: bool) -> None:
    files = list((ROOT / "Tanakh" / "translations").rglob("*"))
    csv_files = sorted(p for p in files if p.suffix.lower() == ".csv")
    xlsx_files = sorted(p for p in files if p.suffix.lower() == ".xlsx")
    for path in csv_files:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                row = next(reader, None)
                if not row:
                    audit.warn("csv_header", f"{path.name}: empty CSV")
                if deep:
                    # Force all rows through the CSV parser without loading them.
                    for _ in reader:
                        pass
        except (OSError, UnicodeError, csv.Error) as exc:
            audit.warn("csv_read", f"{path.name}: {exc}")
    for path in xlsx_files:
        try:
            with zipfile.ZipFile(path) as workbook:
                if "[Content_Types].xml" not in workbook.namelist():
                    audit.error(f"{path.name}: invalid Excel package")
                if deep:
                    bad = workbook.testzip()
                    if bad:
                        audit.error(f"{path.name}: corrupt ZIP member {bad}")
        except (OSError, zipfile.BadZipFile) as exc:
            audit.error(f"{path.name}: unreadable XLSX archive: {exc}")
    audit.stats["translations"] = {
        "csv_files": len(csv_files), "xlsx_files": len(xlsx_files),
        "deep_integrity_check": deep,
    }


def audit_application(audit: Audit) -> None:
    app = (ROOT / "bible_app.html").read_text(encoding="utf-8")
    if 'fetch("gemantria/mappings/gemantria_ciphers.json"' not in app:
        audit.error("Reader references an obsolete cipher data path")
    if "FALLBACK_GREEK_MAP" in app:
        audit.error("Reader refers to an undefined Greek fallback mapping")
    root_toml = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if 'tanakh = "hebrew_bible_cli.cli:app"' not in root_toml:
        audit.error("Root project lacks a working CLI entry point")
    if not (ROOT / "hebrew-bible-cli/src/hebrew_bible_cli/cli.py").exists():
        audit.error("Actual Python CLI package is absent")
    translator = (ROOT / "scripts/translate_tanakh.js").read_text("utf-8")
    if 'path.resolve(__dirname, "..", "Tanakh")' not in translator:
        audit.error("Experimental Greek rendering script has an incorrect corpus path")
    if "--write" not in translator:
        audit.error("Experimental Greek rendering script lacks opt-in write protection")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deep", action="store_true",
                        help="Read every CSV record and test XLSX ZIP checksums")
    parser.add_argument("--output", type=Path, help="Write machine-readable JSON report")
    args = parser.parse_args()
    audit = Audit()
    audit_corpus(audit)
    audit_mappings(audit)
    audit_assets(audit, deep=args.deep)
    audit_application(audit)
    report = audit.report()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if audit.errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
