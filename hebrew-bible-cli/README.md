# Hebrew Bible CLI

CLI tools for Hebrew Tanakh JSON: trope stats, helix visualization, and equation mapping experiments.

## Installation

```bash
cd hebrew-bible-cli
python -m pip install -e .
```

## Usage

After installation, the `hb` command will be available:

```bash
# List books in a JSON file
hb books <path-to-json>

# Inspect first N tokens of a chapter
hb inspect <path-to-json> --book Psalms --chapter 1 --limit 40

# Compute cantillation/trope statistics
hb trope-stats <path-to-json> --book Psalms --chapter 1

# Render double-helix visualization
hb helix <path-to-json> --book Psalms --chapter 1 --out psalm1_helix.png

# Map equations to passages
hb map-eq <path-to-json> --eq "E=mc^2" --book Psalms --top 10
```

## Commands

### books
List book names in a JSON file.

### inspect
Print first N tokens of a book chapter with refs, showing Hebrew text, Strong's numbers, and morphology.

### trope-stats
Compute basic cantillation/stress statistics for a chapter, including:
- Cantillation marks count
- Meteg, Sof Pasuq, Paseq, Maqaf counts
- Average and max trope intensity

### helix
Render a double-helix visualization with:
- Strand A: semantic anchor (Strong's + morphology)
- Strand B: musical/prosodic (trope intensity)

Options:
- `--pitch`: Vertical spacing factor (default: 0.09)
- `--radius`: Base radius (default: 1.0)
- `--link-every`: Draw base-pair line every N tokens (default: 1)

### map-eq
Experimental equation-to-passage mapping. Maps an equation into a feature vector and searches for matching passages based on structural similarity.

This is NOT "proof of encoded physics"—it's a structured similarity search that compares:
- Equation vector: symbolic structure (operators, greek symbols, variables)
- Passage vector: semantic/prosodic structure (Strong's diversity, trope intensity, morphology)

Options:
- `--eq`: Equation string (e.g., 'E=mc^2' or 'S_q=(1-sum p^q)/(q-1)')
- `--book`: Restrict search to a specific book
- `--top`: Number of matches to show (default: 10)
- `--window`: Tokens per passage window (default: 40)

## Examples

```bash
# Using Psalms JSON
hb books ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json
hb trope-stats ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json --book Psalms --chapter 1
hb helix ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json --book Psalms --chapter 1 --out psalm1_helix.png
hb map-eq ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json --eq "E=mc^2" --book Psalms --top 10
```

## Architecture

The CLI is built with:
- **typer**: Command-line interface framework
- **rich**: Beautiful terminal output
- **numpy**: Numerical computations
- **matplotlib**: 3D helix visualization
- **regex**: Enhanced Unicode/Hebrew regex handling

### Modules

- `io.py`: JSON loading and token flattening
- `features.py`: Trope/cantillation analysis (musical layer extraction)
- `helix.py`: Double-helix 3D visualization renderer
- `eqmap.py`: Equation-to-passage similarity search
- `cli.py`: Main CLI commands

## Future Enhancements

1. **Whole-book helix rendering**: Render entire books as smooth 3D models
2. **Enhanced equation mapping**: Use sympy for symbolic parsing + learned embeddings for better matches
3. **PSF framework integration**: Map coherence, disturbance, and perception patterns
