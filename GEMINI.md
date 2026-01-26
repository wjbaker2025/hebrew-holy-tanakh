# Gemini Context: Hebrew Holy Tanakh Repository

## Project Overview

This repository is a comprehensive data collection featuring the **Hebrew Holy Tanakh (Miqra)**. It provides a digitized, parseable version of the Hebrew Bible based on the **Westminster Leningrad Codex (WLC)** (derived from the Leningrad Codex B19a, 1008 CE).

In addition to the biblical text, the repository includes a significant component dedicated to **Gematria** (Jewish numerology), containing cipher specifications, ledgers, and rules for various Gematria systems (Biblical, Reversal, Genesis Order, Standard).

**Primary Purpose:** To serve as a public file storage and data source for the Hebrew Tanakh and Gematria research/applications.

## Directory Structure

### `books/`
Contains the core text of the Tanakh in JSON format. Each file represents a single book.

*   **Format:** JSON
*   **Schema Structure:**
    ```json
    {
      "BookName": {
        "name": "Hebrew Name",
        "chapters": {
          "1": {
            "1": [ // Verse 1
              {
                "strongs": "Strong's Concordance Number",
                "hebrew": "Hebrew Word",
                "english": "English Translation",
                "morphology": "Grammatical Morphology"
              },
              ...
            ]
          }
        }
      }
    }
    ```
*   **Key Files:** `genesis.json`, `exodus.json`, `psalms.json`, etc.

### `gemantria/`
Contains specifications, documentation, and logic definitions for Gematria ciphers.

*   **`gemantria_ciphers.json`**: Machine-readable definitions of various ciphers (Biblical, Reversal, Genesis Order, Standard), including character mappings for Hebrew, Greek, and English.
*   **`CIPHERS.md`**: Human-readable documentation explaining the logic and history behind each cipher.
*   **`ciphers_....js`**: JavaScript files (e.g., `ciphers_2026-01-13_12-36-32.js`) containing cipher definitions and configuration options, likely used by a calculator tool or frontend interface.
*   **`shematria_rules.json`**: Rules for "Shematria" (likely a specific sub-system or variation).
*   **`gematria_ledger.json` & `word_gematria_ledger.json`**: Data files mapping words or phrases to their calculated Gematria values.

## Key Files

*   **`README.md`**: The primary entry point, describing the repository's intent and sources (WLC).
*   **`LICENSE`**: MIT License.

## Usage Guide

This repository is primarily a **data source**.

1.  **Text Analysis:** Parse the files in `books/` to extract Hebrew text, English translations, or morphological data for linguistic analysis or display.
2.  **Gematria Calculation:** Use `gemantria/gemantria_ciphers.json` or the logic in the `.js` files to implement Gematria calculators or validation tools.
3.  **Study:** The `CIPHERS.md` file serves as a reference for understanding different Gematria systems.

## Development Notes

*   **No Build System:** As a data repository, there are no standard build scripts (like `npm run build` or `make`) in the root.
*   **Data Integrity:** When modifying JSON files, ensure strictly valid JSON syntax is maintained.
*   **Conventions:**
    *   **Text:** Follows the WLC transcription.
    *   **Ciphers:** Defined with specific mappings for Hebrew, Greek, and English.
