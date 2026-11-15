# The Hebrew Holy Tanakh (Miqra)

This repository provides a digitized, parseable version of the Hebrew Bible (Tanakh) based on the Westminster Leningrad Codex (WLC), a digital transcription of the Leningrad Codex (B19a) from 1008 CE. It includes structured JSON files for each biblical book with morphological parsing, alongside comprehensive gematria analysis tools, cipher systems, and multiscript mappings for numerical and symbolic study of the text.

## Repository Structure

- `Tanakh/`: 39 numbered Hebrew biblical book JSON files and a separate `translations/` asset collection.
- `gemantria/mappings/gemantria_ciphers.json`: authoritative numeric cipher data, including traditional tables and explicitly labeled proposed models.
- `gemantria/mappings/`: separate cross-script correspondences and experimental symbolic metadata.
- `gemantria/scripts/`: historical calculator resources; not all are standalone modules.
- `hebrew-bible-cli/`: installable Python CLI. The root package also exposes it as `tanakh`.
- `scripts/`: corpus audit, Unicode-safe gematria scoring, legacy Greek-letter rendering, and read-only pinned WLC consonantal collation.
- `tests/` and `.github/workflows/repository-audit.yml`: regression checks and read-only integrity auditing.
- `bible_app.html`: web reader; serve over HTTP to enable local JSON fetches.
- `docs/`: historical/research status, cipher details, and audit notes.

## Provenance and interpretation

The Hebrew JSON files are a derivative digital corpus attributed to the Westminster Leningrad Codex, not scans of an autograph or a guarantee of exact word-level agreement. External source collation is separate from structural validation. The field `hebrew_greek` is a legacy Greek-glyph **substitution of Hebrew**, not reliably value-preserving, NOT the Greek Septuagint or a translation.

Standard Hebrew Mispar Hechrechi, traditional Greek isopsephy, and traditional Syriac numeral values are distinct from the proposed Biblical, reversal, Genesis-order, and Greek-transposition models. Never infer historical authorship or intended encryption from a numerical match alone.

Read [repository audit and outstanding manuscript checks](docs/REPOSITORY_AUDIT_2026-11-14.md) before using numerical data as textual evidence.

## Key Features

- **Digitized Text**: Complete Hebrew Bible in parseable JSON format.
- **Gematria Analysis**: Multiple cipher systems for numerical analysis of Hebrew text.
- **Multiscript Support**: Mappings across different alphabets and scripts.
- **Physics Integration**: Symbolic connections between letters and physical concepts.
- **Morphological Parsing**: Detailed grammatical analysis with Strong's numbers.

## Usage

### Text Analysis

Parse verses by iterating through word arrays and applying gematria calculations using specified ciphers.

### Cipher Selection

- Use `standard` for conventional Hebrew numerical comparisons.
- Select `biblical` explicitly for the experimental Shin=3, Tav=4 reconstruction.
- Use `greek_isopsephy` for conventional Greek and `syriac_standard` for traditional Syriac.
- Compare models separately, recording the exact text witness, spelling and normalization.

### Data Integrity

All files maintain strict JSON structure and preserve morphological tags. Recent consolidations have merged overlapping data into single sources of truth to prevent redundancy while preserving all information.

## Contributing

Contributions are welcome. Please ensure any modifications maintain data integrity and follow the established structure.

## License

See LICENSE file for details.

## Manuscript-text collation

Run `py -m scripts.collate_wlc --output wlc-collation.json` from the repository root on Windows 11 to compare all 39 local books against the pinned [Open Scriptures WLC revision](https://github.com/openscriptures/morphhb/tree/d4265dfa93b78d82765a557e12d965528c17c1a9/wlc). The process is read-only: it records differing consonant sequences and missing or extra verses without altering the corpus. It does not establish niqqud, cantillation, ketiv/qere segmentation, Strong's metadata, English-gloss accuracy, or an ancient manuscript autograph. The source text and morphological metadata have their own licensing and attribution.
