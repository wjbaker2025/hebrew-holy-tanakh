# Installation and Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Quick Install

From the repository root:

```bash
cd hebrew-bible-cli
python -m pip install -e .
```

The `-e` flag installs in "editable" mode, which is useful for development.

## Verifying Installation

After installation, verify the CLI is available:

```bash
hb --help
```

You should see the help menu with all available commands.

## Dependencies

The following packages will be automatically installed:

- **typer** (>=0.12.3) - CLI framework
- **rich** (>=13.7.1) - Terminal output formatting
- **numpy** (>=1.26.4) - Numerical computations
- **matplotlib** (>=3.8.4) - 3D visualization
- **regex** (>=2024.5.15) - Enhanced Unicode/regex support

## Testing the Installation

Run a quick test:

```bash
cd ..  # Go back to repository root
hb books Tanakh/3.\ Ketuvim\ -\ Writings/27_psalms.json
```

Expected output: `Psalms`

## Troubleshooting

### Command not found

If `hb` is not found after installation, ensure your Python user bin directory is in your PATH:

```bash
# On Linux/Mac
export PATH="$HOME/.local/bin:$PATH"

# On Windows
# Add %APPDATA%\Python\Python3XX\Scripts to your PATH
```

### Permission errors

If you get permission errors during installation, use the `--user` flag:

```bash
python -m pip install --user -e .
```

### Import errors

If you get import errors when running commands, ensure all dependencies are installed:

```bash
python -m pip install typer rich numpy matplotlib regex
```

## Uninstalling

To remove the CLI tool:

```bash
python -m pip uninstall hebrew-bible-cli
```

## Development Setup

For development with additional tools:

```bash
# Install in editable mode
python -m pip install -e .

# Optional: Install development tools
python -m pip install pytest black ruff mypy
```

## Using with Virtual Environments

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install the CLI
pip install -e .
```

## Next Steps

After installation, see:
- `README.md` for basic usage
- `EXAMPLES.md` for comprehensive examples
- Run `hb --help` for command reference
