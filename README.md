# The Hebrew Holy Tanakh (Miqra)

This repository provides a digitized, parseable version of the Hebrew Bible (Tanakh) based on the Westminster Leningrad Codex (WLC), a digital transcription of the Leningrad Codex (B19a) from 1008 CE. It includes structured JSON files for each biblical book with morphological parsing, alongside comprehensive gematria analysis tools, cipher systems, and multiscript mappings for numerical and symbolic study of the text.

## Repository Structure

```
├───.github
│   ├───agents
│   └───copilot-instructions.md
├───gemantria
│   ├───client
│   │   ├───cipher_builder.js
│   │   └───ciphers_2026-01-13_12-36-32.js
│   ├───definitions
│   │   ├───gemantria_ciphers.json
│   │   └───shematria_rules.json
│   ├───docs
│   │   ├───CIPHERS.md
│   │   ├───PHYSICS_MAP.md
│   │   ├───Place Order Scenock Table.md
│   │   └───place_order_scenock_table.json
│   ├───images
│   │   ├───gates_of_the_palaces.jpg
│   │   └───the_seven_palaces.jpg
│   └───mappings
│       ├───alphabet_map.json
│       ├───gematria_multiscript_map.json
│       └───hebrew_parsing_tag_legend.json
├───Tanakh
│   ├───1. Torah - Instructions
│   │   ├───01_genesis.json
│   │   ├───02_exodus.json
│   │   ├───03_leviticus.json
│   │   ├───04_numbers.json
│   │   └───05_deuteronomy.json
│   ├───2. Nevi'im - Prophets
│   │   ├───1. Former Prophets
│   │   │   ├───06_joshua.json
│   │   │   ├───07_judges.json
│   │   │   ├───08_1_samuel.json
│   │   │   ├───09_2_samuel.json
│   │   │   ├───10_1_kings.json
│   │   │   └───11_2_kings.json
│   │   ├───2. Latter Prophets
│   │   │   ├───12_isaiah.json
│   │   │   ├───13_jeremiah.json
│   │   │   └───14_ezekiel.json
│   │   └───3. Minor Prophets
│   │       ├───15_hosea.json
│   │       ├───16_joel.json
│   │       ├───17_amos.json
│   │       ├───18_obadiah.json
│   │       ├───19_jonah.json
│   │       ├───20_micah.json
│   │       ├───21_nahum.json
│   │       ├───22_habakkuk.json
│   │       ├───23_zephaniah.json
│   │       ├───24_haggai.json
│   │       ├───25_zechariah.json
│   │   │       └───26_malachi.json
│   └───3. Ketuvim - Writings
│       ├───27_psalms.json
│       ├───28_proverbs.json
│       ├───29_job.json
│       ├───30_song_of_solomon.json
│       ├───31_ruth.json
│       ├───32_lamentations.json
│       ├───33_ecclesiastes.json
│       ├───34_esther.json
│       ├───35_daniel.json
│       ├───36_ezra.json
│       ├───37_nehemiah.json
│       ├───38_1_chronicles.json
│       └───39_2_chronicles.json
├───.gitignore
├───bootstraps.ps1
├───bible_app.html
├───GEMINI.md
├───get_tree.ps1
├───LICENSE
├───pyproject.toml
├───README.md
└───tree.md
```

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

- Default to "biblical" cipher for Tanakh analysis.
- Use "standard" for general Hebrew gematria.

### Data Integrity

All files maintain strict JSON structure and preserve morphological tags. Recent consolidations have merged overlapping data into single sources of truth to prevent redundancy while preserving all information.

## Contributing

Contributions are welcome. Please ensure any modifications maintain data integrity and follow the established structure.

## License

See LICENSE file for details.
