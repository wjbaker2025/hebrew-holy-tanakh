# Reorganization Plan

## Status

One open PR: `copilot/create-hebrew-bible-cli` — all new files in `hebrew-bible-cli/`, no conflicts.
Stale remote branch: `copilot/enhance-gemantria-functionality` — PR closed on GitHub, safe to ignore.

## Uncommitted Local Changes (already done, need committing)

| Action   | From                                                 | To                                          |
| -------- | ---------------------------------------------------- | ------------------------------------------- |
| Moved    | `gemantria/client/`                                  | `gemantria/scripts/`                        |
| Moved    | `gemantria/definitions/gemantria_ciphers.json`       | `gemantria/mappings/gemantria_ciphers.json` |
| Moved    | `gemantria/definitions/shematria_rules.json`         | `gemantria/mappings/shematria_rules.json`   |
| Moved    | `gemantria/docs/` (CIPHERS.md, PHYSICS_MAP.md, etc.) | `docs/`                                     |
| Moved    | `gemantria/docs/place_order_scenock_table.json`      | `gemantria/mappings/`                       |
| Moved    | `translate_tanakh.js`                                | `scripts/`                                  |
| Deleted  | `bible_app.html` (moved to `.local/`)                | —                                           |
| Modified | `.gitignore`, `GEMINI.md`, `.vscode/settings.json`   | —                                           |

## Remaining Cleanup (to do after merging open PR)

1. **Rename** `docs/Place Order Scenock Table.md` → `docs/place_order_scenock_table.md` (spaces → underscores)
2. **Create** `tests/.gitkeep` (pytest is configured but no tests/ folder exists)
3. **Update** `README.md` — tree listing is stale (still shows old `gemantria/client/`, `gemantria/definitions/`, `gemantria/docs/` structure)
4. **Update** `.github/copilot-instructions.md` — references `bootstraps.ps1` at root (still correct) and old folder names
5. **Merge** `copilot/create-hebrew-bible-cli` PR

## Suggested Commit Order

1. Merge open PR on GitHub
2. `git pull` to get PR merge commit
3. Commit all current working tree changes as: `refactor: reorganize gemantria folder structure`
4. Apply remaining cleanup items above
5. Commit as: `chore: rename docs, update README tree, add tests folder`
