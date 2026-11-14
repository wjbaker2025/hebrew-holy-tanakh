# Repository integrity audit and textual provenance

**Audit date:** 2026-11-14  
**Target:** `wjbaker2025/hebrew-holy-tanakh`, main baseline `e200661d61e6bd2b717a927ff0135e7d14eb3c92`  
**Change policy:** Correct demonstrable implementation errors; preserve experimental models with honest labels; do not alter canonical Hebrew tokens without collation to a specific upstream witness.

## Inventory and scope

GitHub's nontruncated recursive tree contains **116 tracked entries**, including directories, **39 numbered book JSON files**, **3 CSV translation tables**, **8 XLSX translation assets**, a standalone HTML reader, Python CLI, gematria mappings, JavaScript calculator resources, documentation, PowerShell bootstrap utilities, and auxiliary audio CSVs. The number of tracked entries is *not* a count of files, errors, or verified manuscript readings.

The new `scripts/audit_repository.py` reads all 39 books and mapping JSON files and checks their JSON syntax, canonical book-number sequence, verse/token shape, Unicode source fields, primary/duplicated cipher metadata, numeric Greek sigma variants, declared Syriac table, local application paths, and translation file integrity. `--deep` walks the full CSV records and tests XLSX ZIP CRCs. Reports include the **whole-source SHA-256 hash** of the ordered 39 source files. All auditing is read-only.

The GitHub Actions workflow runs the audit and produces a downloadable machine-readable report. The workflow and reports must be reviewed before merging. This record documents the approach and individual source-reviewed defects; it is **not** a claim that all historical words or translation glosses have been independently authenticated.

## Confirmed fixes in this pull request

| Area | Confirmed baseline defect | Proposed correction |
| --- | --- | --- |
| Cipher metadata | Conventional and proposed schemes were conflated | Label historical tables separately from speculative/model tables without changing the model's Shin=3/Tav=4 assignments |
| Greek model | Ordinary sigma was missing; case/final/lunate variants differed | Add σ, ς, ϲ and numerical variants to the experimental transposition |
| Greek historical | No distinct canonical Greek isopsephy mapping in the primary cipher table | Add historical Greek values including sampi=900, separate from experimental sampi=90 |
| Syriac | No independent Syriac script value table | Add traditional 22-letter Syriac numeral values |
| Duplicated metadata | Beta reversal was 200 in one field, 100 in another | Make the proposed reversal field consistent (200) |
| HTML reader | Fetched non-existent `gemantria/definitions/` mapping; referred to undefined Greek fallback | Point to maintained `gemantria/mappings/` and use explicit script-specific maps |
| HTML reader | Corrupted duplicated `loadBook` code, redundant retry path, and unsafe interpolation of word values | Restore single book loading flow, remove unreachable branches, escape displayed text |
| Hebrew-to-Greek renderer | Used nonexistent `scripts/Tanakh` path and rewrote every file by default | Use repository `Tanakh/`, report only by default, require explicit `--write`, and compare against the corpus’s actual legacy glyph conventions |
| Python root package | Entry point pointed to missing `hebrew_holy_tanakh.cli`; package directory was absent | Install actual `hebrew_bible_cli` package; do not bundle large source corpus in wheel |
| Equation ranking | Equal similarity scores caused heap comparisons of dictionaries | Add integer tiebreak and validate positive window and result counts |
| Reproducibility | No tracked regression suite / CI integrity audit | Add Unicode-safe scorer, tests, read-only asset audit, and CI |

## Numerical models and textual witness discipline

- `standard` is conventional Hebrew Mispar Hechrechi. Five final Hebrew letters normalize to their base forms for this model.
- `greek_isopsephy` is conventional Greek isopsephy: traditional spelling Ἰησοῦς = **888**, regardless of final sigma or uncial/lunate sigma transcription.
- `syriac_standard` is a traditional Syriac letter-number table. It does not establish what language Jesus spoke in a specific scene, nor the spelling of an autograph.
- `biblical` (Shin=3, Tav=4), `reversal`, `genesis_order`, and `greek_transposition` are **explicitly proposed/experimental project models**. Under the latter, Ἰησοῦς = **492**. That difference is expected and does not invalidate a model by itself.
- The `genesis_order` sequence is NOT the literal sequence of first Hebrew consonants encountered in Genesis 1:1. The opening consonant sequence is ב ר א ש י ת.
- `hebrew_greek` is a legacy glyph substitution of Hebrew script, not guaranteed to preserve even the proposed Hebrew numeric values (notably ו → υ). Do NOT cite it as an extant Septuagint Greek text, translation, Greek papyrus, or independent Gospel witness.
- A numerical equality across Hebrew, Greek, or Aramaic witnesses is meaningful only after recording the exact reading, manuscript/edition, variant scope, normalization and precommitted scoring rules.

### First full-corpus audit result

The first GitHub Actions audit parsed **39 book files, 929 chapters, 23,144 verse rows, and 298,947 word records**. It found **zero structural errors** and two data warnings: the malformed verse key `Isaiah 64:NaN` and nonsequential verse identifiers in Nehemiah 7. It checked 7 mapping JSON files, 3 CSV translations and the complete ZIP CRCs of 8 XLSX translation assets. The ordered 39-file source-bytes SHA-256 fingerprint was:

`7b8ac76ccaa363c979d709114ff38a40952fe02d6304c87bbb8dc0760c98955e`

These two verse-key issues require upstream source comparison before repair. The initial source validation passed despite warnings; the packaging job reported a separate metadata error which was corrected on the audit branch and must pass its next CI run.

### Known textual discrepancies requiring separate source collation

A prior targeted comparison of local **1 Kings 17** consonant tokens to Open Scriptures **WLC 4.20** reported the following apparent missing words in the local derivative corpus:

| Verse | Reported missing Hebrew |
| --- | --- |
| 1 Kings 17:17 | בו |
| 1 Kings 17:18 | לי ולך |
| 1 Kings 17:19 | לי |

These are **previously documented sample differences**, not yet repaired or reverified against an independent facsimile as part of this PR. They are not automatically ancient variant readings. Before correcting them, verify upstream verse segmentation, word-level metadata and morphology and preserve the evidence and original corpus hash. The full 39-book corpus has **not** yet been externally collated against WLC at every token. This distinction is essential.

Other necessary provenance reviews include translator/editor rights and versions for the BSB and other modern/printed translation assets, completeness of Hebrew poetic verse numbering, accent/cantillation fidelity, and a manuscript-witness register for Aramaic/Greek quotations used in research.

## Reproducible commands (Windows 11, PowerShell)

Run these from the repository root with Python 3.12+ and Node.js installed:

```powershell
py -m unittest discover -s tests -v
py -m scripts.audit_repository --deep --output audit-report.json
py -m scripts.gematria_score "Ἰησοῦς" --script greek --cipher greek_isopsephy
py -m scripts.gematria_score "ܐܣܐ" --script syriac --cipher syriac_standard
node scripts/translate_tanakh.js --check
```

The last command reports disagreements between existing `hebrew_greek` annotations and the existing legacy glyph substitution convention; it does **not** rewrite the corpus. Only the explicit `--write` flag changes data. Do not run `--write` to force agreement with a hypothesis before inspecting the reported differences.

To inspect the HTML reader, serve the repository through a local HTTP server; `file://` does not reliably allow its browser `fetch` requests.

## Remaining verification work

This PR repairs the auditable tooling and adds whole-repository structural checks. A **full scholarly proof of corpus fidelity** additionally requires selecting and preserving external witnesses, acquiring source images where possible, collating each verse (including ketiv/qere, cantillation and tokenization), and publishing a reviewed apparatus of substantive differences before modifying corpus bytes. The same restriction applies to translations and experimental symbolic associations.

**Merge criterion:** CI checks pass; source assets have not been silently rewritten; proposed-model status is explicit; errors and warnings from the machine-readable audit report are reviewed and assigned to documented follow-up work.

## Pinned WLC consonantal collation (additional independent job)

The PR adds `scripts/collate_wlc.py` and a third CI job that downloads the 39 OSHB/WLC XML books from the **pinned** Open Scriptures revision `d4265dfa93b78d82765a557e12d965528c17c1a9` (2026-11-11), and records letter-only matches, divergences, missing verses, extra verses and ketiv/qere alternatives. This is a read-only source-to-source comparison, and its `wlc-collation.json` report is uploaded as an Actions artifact. The WLC text is public domain; Open Scriptures morphology carries CC BY 4.0 attribution. The exact status and discrepancy counts must be read from the completed workflow artifact; no total is asserted before verification. A consonant match does not verify accentuation, punctuation, morphology, translations, manuscript dating or authorial intent.
