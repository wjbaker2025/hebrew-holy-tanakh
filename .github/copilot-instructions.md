# Copilot Instructions for Hebrew Holy Tanakh Repository

## Project Overview

This repository contains the digitized Hebrew Bible (Tanakh) structured as parseable JSON, alongside advanced gematria analysis tools. It is a polyglot environment using **JSON** for data, **Python (3.12+)** for backend tooling, and **JavaScript** for frontend/UI logic.

## Architecture & Data Structure

- **Core Data (`books/`)**:
  - Format: `{"BookName": {"chapters": {"1": {"1": [WordObjects...]}}}}`
  - Word Object: `{"strongs": "1234", "hebrew": "...", "english": "...", "morphology": "..."}`
  - invariant: Maintain strict JSON structure and preservation of morphological tags.

- **Gematria Engine (`gemantria/`)**:
  - **SSOT**: `gemantria_ciphers.json` (Version 5.0) is the SINGLE SOURCE OF TRUTH for all cipher logic.
  - **Legacy**: `cipher_spec.json` is legacy; prefer `gemantria_ciphers.json`.
  - **UI Mirror**: `ciphers_*.js` (e.g., `ciphers_2026-01-13_12-36-32.js`) mirrors valid ciphers for UI apps.
  - **Mappings**: `gematria_multiscript_map.json` handles cross-script (Hebrew/Greek/Arabic) logic.

## Workflows

- **Environment Setup**:
  - Run `.\bootstraps.ps1` to initialize.
  - **CRITICAL**: The project expects a portable Python installation at `../../Programming/WPy64-31241/...` relative to root. If running locally without this, ensure `python` is 3.12+ and available.

- **Frontend/UI Logic**:
  - When updating ciphers in `ciphers_*.js`, use the `new cipher(...)` constructor.
  - **Convention**: Set HSL color values to `0, 0, 0` (Neutralized) for all new ciphers.
  - Example: `new cipher("Name", "Category", 0, 0, 0, [chars], [values], ...)`

## Development Patterns

- **Scripting**: Use Powershell (`.ps1`) for orchestration and Python for data processing.
- **Testing**: `pyproject.toml` defines `pytest`, `ruff`, and `black` configuration. Run tests before committing data changes.
- **Cipher Updates**:
  1. Define in `gemantria_ciphers.json` (The Source).
  2. If UI support is needed, mirror specific fields to `ciphers_*.js` (The View).
  3. Ensure mappings exist in `gematria_multiscript_map.json`.

## Key Files

- `bootstraps.ps1`: Environment init.
- `gemantria/gemantria_ciphers.json`: Primary Logic Definition.
- `books/genesis.json`: Canon structure reference.
