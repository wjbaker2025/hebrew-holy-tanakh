# Hebrew Bible CLI - Examples

This document provides comprehensive examples of using the `hb` CLI tool.

## Installation

```bash
cd hebrew-bible-cli
python -m pip install -e .
```

## Basic Examples

### 1. List Books in a JSON File

```bash
hb books ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json
# Output: Psalms

hb books ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json
# Output: Genesis
```

### 2. Inspect Tokens in a Chapter

View the first 10 tokens of Psalms chapter 1:

```bash
hb inspect ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json --book Psalms --chapter 1 --limit 10
```

This displays a table with:
- Token number
- Reference (book:chapter:verse)
- Hebrew text (with cantillation marks)
- Strong's concordance number
- Morphological analysis

### 3. Compute Trope Statistics

Analyze the cantillation marks (te'amim) in Genesis chapter 1:

```bash
hb trope-stats ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json --book Genesis --chapter 1
```

Output includes:
- Total tokens
- Cantillation marks count and per-token average
- Meteg, Sof Pasuq, Paseq, Maqaf counts
- Average and maximum trope intensity

### 4. Generate Double-Helix Visualization

Create a 3D visualization of Psalm 1:

```bash
hb helix ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json \
  --book Psalms \
  --chapter 1 \
  --out psalm1_helix.png \
  --pitch 0.09 \
  --radius 1.0 \
  --link-every 2
```

This creates a double-helix PNG where:
- **Strand A**: Semantic anchor (Strong's numbers + morphology)
- **Strand B**: Musical/prosodic layer (trope intensity)

Parameters:
- `--pitch`: Controls vertical spacing (smaller = tighter helix)
- `--radius`: Base radius of the helix
- `--link-every`: Draw connecting lines every N tokens (use higher values for less clutter)

### 5. Map Equations to Passages

Search for passages that structurally match Einstein's mass-energy equation:

```bash
hb map-eq ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json \
  --eq "E=mc^2" \
  --book Psalms \
  --top 10
```

Try a more complex equation (Rényi entropy):

```bash
hb map-eq ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json \
  --eq "S_q=(1-sum p^q)/(q-1)" \
  --top 5
```

This experimental feature:
1. Parses the equation into a structural feature vector (operators, symbols, variables)
2. Creates passage vectors from sliding windows of tokens (semantic + prosodic features)
3. Computes cosine similarity scores
4. Returns top matches with preview text

**Note**: This is NOT claiming "encoded physics" - it's a structured similarity search tool that can reveal interesting textual patterns.

## Advanced Examples

### Analyzing Entire Books

Generate statistics for all chapters in Psalms:

```bash
for i in {1..150}; do
  echo "=== Psalm $i ==="
  hb trope-stats ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json --book Psalms --chapter $i 2>/dev/null || echo "Chapter $i not found"
done
```

### Custom Helix Visualizations

Create a tight helix with minimal connections:

```bash
hb helix ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json \
  --book Genesis \
  --chapter 1 \
  --out genesis1_tight.png \
  --pitch 0.05 \
  --radius 0.8 \
  --link-every 5
```

Create a loose, expanded helix:

```bash
hb helix ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json \
  --book Genesis \
  --chapter 1 \
  --out genesis1_loose.png \
  --pitch 0.15 \
  --radius 1.5 \
  --link-every 1
```

### Equation Mapping Experiments

Search across all Genesis for wave equation patterns:

```bash
hb map-eq ../Tanakh/1.\ Torah\ -\ Instructions/01_genesis.json \
  --eq "d^2u/dt^2=c^2*d^2u/dx^2" \
  --top 15 \
  --window 50
```

Find passages matching Schrödinger's equation structure:

```bash
hb map-eq ../Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json \
  --eq "iℏ∂Ψ/∂t=HΨ" \
  --book Psalms \
  --top 20
```

## Understanding the Output

### Trope Intensity Scoring

The tool calculates "trope intensity" as a composite score:
- Each cantillation mark: +1.0
- Meteg mark: +0.5
- Punctuation (sof pasuq, paseq): +0.5
- Maqaf (connector): +0.2

This provides a quantitative measure of the musical/prosodic complexity of each token.

### Helix Visualization Interpretation

The double-helix visualization represents two complementary information strands in the Hebrew text:

1. **Semantic Strand** (Strand A):
   - Thickness varies with Strong's number magnitude
   - Represents lexical/semantic content
   - Color typically blue in default matplotlib

2. **Prosodic Strand** (Strand B):
   - Thickness varies with trope intensity
   - Represents musical/cantillation layer
   - Color typically orange in default matplotlib

The "twist rate" is modulated by prosodic intensity, creating visual patterns that correlate with the text's rhythmic structure.

### Equation Mapping Scores

Similarity scores range from 0.0 (no match) to 1.0 (perfect match):
- **0.6+**: Strong structural similarity
- **0.5-0.6**: Moderate similarity
- **0.4-0.5**: Weak similarity
- **<0.4**: Minimal similarity

The algorithm compares:
- Equation features: operators, Greek symbols, variables, structural complexity
- Passage features: Strong's diversity, morphological variety, prosodic dynamics

## Tips and Tricks

1. **Large Visualizations**: For longer chapters (100+ verses), increase `--link-every` to 10 or more to reduce visual clutter.

2. **Finding Patterns**: Use smaller window sizes (e.g., `--window 20`) for finer-grained equation mapping.

3. **Performance**: The `map-eq` command can be slow on large books. Restrict searches with `--book` parameter when possible.

4. **Hebrew Display**: Ensure your terminal supports Hebrew Unicode characters for best results with the `inspect` command.

## Future Enhancements

Planned features include:
- Whole-book helix rendering with smooth interpolation
- Sympy integration for advanced symbolic equation parsing
- Machine learning embeddings for better passage matching
- PSF (Perception-Structure-Function) framework integration
- Export to 3D model formats (OBJ, STL) for helix visualizations
