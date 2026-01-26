# The Hebrew Holy Tanakh (Miqra)

This repository provides a digitized, parseable version of the Hebrew Bible (Tanakh) based on the Westminster Leningrad Codex (WLC), a digital transcription of the Leningrad Codex (B19a) from 1008 CE. It includes structured JSON files for each biblical book with morphological parsing, alongside comprehensive gematria analysis tools, cipher systems, and multiscript mappings for numerical and symbolic study of the text.

## Repository Structure

### `books/`

Contains JSON files for each book of the Tanakh, structured hierarchically:

- `book > chapters > verses > words[]`
- Each word object includes: `strongs`, `hebrew`, `english`, `morphology`

Example structure:

```json
{
  "Genesis": {
    "chapters": {
      "1": {
        "1": [
          {
            "strongs": "7225",
            "hebrew": "בְּרֵאשִׁ֖ית",
            "english": "In the beginning",
            "morphology": "Preposition-b :: Noun - feminine singular"
          }
        ]
      }
    }
  }
}
```

### `gemantria/`

Contains gematria calculation resources and analysis tools:

- **`alphabet_map.json`**: Core Hebrew letter mappings with Greek equivalents, physics, pneumatic, and theurgy data. Includes symbolic mappings and metadata.
- **`gemantria_ciphers.json`**: Comprehensive cipher definitions including Biblical, Reversal, Genesis Order, Standard, and Greek ciphers.
- **`gematria_multiscript_map.json`**: Multiscript gematria mappings across Hebrew, Greek, Arabic, and English alphabets.
- **`word_gematria_ledger.json`**: Pre-computed gematria values for words.
- **`ciphers_2026-01-13_12-36-32.js`**: JavaScript configuration for cipher implementations.
- **`PHYSICS_MAP.md`**: Single source of truth for Greek letter to physics/pneumatic role mappings.
- **`CIPHERS.md`**: Documentation for available ciphers.
- **`hebrew_parsing_tag_legend.json`**: Legend for Hebrew morphological parsing tags.
- **`shematria_rules.json`**: Rules for shematria calculations.
- **`pneumatic_spec.json`**: Advanced mappings linking Hebrew letters to physics concepts and Greek equivalents.
- Additional files: Images and supplementary documentation.

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
