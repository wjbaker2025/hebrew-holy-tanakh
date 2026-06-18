# Copilot Instructions for Hebrew Holy Tanakh Repository

## Project Overview

This repository contains the digitized Hebrew Bible (Tanakh) structured as parseable JSON, alongside advanced gematria analysis tools. It is a polyglot environment using **JSON** for data, **Python (3.12+)** for backend tooling, and **JavaScript** for frontend/UI logic.

## Architecture & Data Structure

- **Core Data (`Tanakh/`)**:
  - Format: `{"BookName": {"chapters": {"1": {"1": [WordObjects...]}}}}`
  - Word Object: `{"strongs": "1234", "hebrew": "...", "english": "...", "morphology": "..."}`
  - invariant: Maintain strict JSON structure and preservation of morphological tags.
  - Do not add, rename, or remove fields from the Word Object schema without explicit user instruction. If asked to modify the schema, warn the user that all existing Tanakh JSON files would require migration and request confirmation before proceeding.

- **Gematria Engine (`gemantria/`)**:
  - Note: the directory is intentionally spelled `gemantria/` to match the repository on disk.
  - **SSOT**: `gemantria_ciphers.json` (Version 5.0) is the SINGLE SOURCE OF TRUTH for all cipher logic.
  - **Legacy**: `cipher_spec.json` is legacy. Do NOT write to or derive logic from `cipher_spec.json` under any circumstances.
  - **UI Mirror**: `ciphers_*.js` (e.g., `ciphers_2026-01-13_12-36-32.js`) mirrors valid ciphers for UI apps. Always edit the single most recently timestamped `ciphers_*.js` file. Do not create a new timestamped file unless explicitly instructed to do so.
  - **Mappings**: `gematria_multiscript_map.json` handles cross-script (Hebrew/Greek/Arabic) logic.

## Workflows

- **Environment Setup**:
  - Run `.\bootstraps.ps1` to initialize.
  - **CRITICAL**: The project expects a portable Python installation at `../../Programming/WPy64-31241/...` relative to root. If running locally without this, ensure `python` is 3.12+ and available.
  - If you detect scripts that hardcode the portable Python path and the path does not exist in the current environment, flag the path to the user and suggest substituting the system python3 binary. Do not silently rewrite hardcoded paths without user confirmation.

- **Frontend/UI Logic**:
  - When updating ciphers in `ciphers_*.js`, use the `new cipher(...)` constructor.
  - **Convention**: Set HSL color values to `0, 0, 0` (Neutralized) for all new ciphers.
  - Example: `new cipher("Name", "Category", 0, 0, 0, [chars], [values], ...)`

## Development Patterns

- **Scripting**: Use Powershell (`.ps1`) for orchestration and Python for data processing.
- **Testing**: `pyproject.toml` defines `pytest`, `ruff`, and `black` configuration. Run tests before committing data changes.
- **Cipher Updates**:
  1. Define in `gemantria_ciphers.json` (The Source).
  2. If the user does not specify whether UI support is needed when requesting a cipher update, ask: "Should this cipher also be mirrored to the UI JavaScript file?" before proceeding with step 2.
  3. If UI support is needed, mirror only the following fields to the most recently timestamped `ciphers_*.js` file (The View): name, category, characters array, and values array. Do not mirror internal metadata fields such as version or audit logs.
  4. If the cipher includes non-Hebrew characters (Greek, Arabic), ensure a corresponding entry exists in `gematria_multiscript_map.json`. For Hebrew-only ciphers, no mapping update is required.

## Key Files

- `bootstraps.ps1`: Environment init.
- `gemantria/gemantria_ciphers.json`: Primary Logic Definition.
- `Tanakh/1. Torah - Instructions/01_genesis.json`: Canon structure reference.
