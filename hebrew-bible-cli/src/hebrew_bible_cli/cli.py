from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .io import load_json, list_books, flatten_tokens
from .features import trope_stats_for_tokens
from .helix import render_helix_png
from .eqmap import map_equation_to_passages

app = typer.Typer(add_completion=False)
console = Console()


@app.command("books")
def cmd_books(path: str = typer.Argument(..., help="Path to a Tanakh JSON file.")):
    """List book names in the JSON file."""
    doc = load_json(path)
    books = list_books(doc)
    for b in books:
        console.print(b)


@app.command("inspect")
def cmd_inspect(
    path: str = typer.Argument(..., help="Path to a Tanakh JSON file."),
    book: str = typer.Option(..., "--book", "-b", help="Book name (e.g., Psalms)."),
    chapter: str = typer.Option("1", "--chapter", "-c", help="Chapter number as string, e.g. '1'."),
    limit: int = typer.Option(40, "--limit", "-n", help="Number of tokens to print."),
):
    """Print first N tokens of a book chapter with refs."""
    doc = load_json(path)
    tokens = flatten_tokens(doc, book=book, chapter=chapter)

    table = Table(title=f"{book} chapter {chapter} (first {min(limit, len(tokens))} tokens)")
    table.add_column("#", justify="right")
    table.add_column("Ref")
    table.add_column("Hebrew")
    table.add_column("Strongs", justify="right")
    table.add_column("Morphology")

    for i, t in enumerate(tokens[:limit], start=1):
        table.add_row(str(i), t["ref"], t["hebrew"], str(t["strongs"]), t["morphology"])

    console.print(table)


@app.command("trope-stats")
def cmd_trope_stats(
    path: str = typer.Argument(..., help="Path to a Tanakh JSON file."),
    book: str = typer.Option(..., "--book", "-b", help="Book name (e.g., Psalms)."),
    chapter: str = typer.Option("1", "--chapter", "-c", help="Chapter number."),
):
    """Compute basic cantillation/stress statistics for a chapter."""
    doc = load_json(path)
    tokens = flatten_tokens(doc, book=book, chapter=chapter)
    stats = trope_stats_for_tokens(tokens)

    table = Table(title=f"Trope Stats — {book} {chapter}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for k, v in stats.items():
        table.add_row(k, str(v))
    console.print(table)


@app.command("helix")
def cmd_helix(
    path: str = typer.Argument(..., help="Path to a Tanakh JSON file."),
    book: str = typer.Option(..., "--book", "-b", help="Book name."),
    chapter: str = typer.Option("1", "--chapter", "-c", help="Chapter number."),
    out: str = typer.Option("helix.png", "--out", "-o", help="Output PNG path."),
    pitch: float = typer.Option(0.09, "--pitch", help="Vertical spacing factor."),
    base_r: float = typer.Option(1.0, "--radius", help="Base radius."),
    link_every: int = typer.Option(1, "--link-every", help="Draw base-pair line every N tokens."),
):
    """Render a double-helix visualization (semantic strand vs musical/prosody strand)."""
    doc = load_json(path)
    tokens = flatten_tokens(doc, book=book, chapter=chapter)
    render_helix_png(tokens, out_path=out, pitch=pitch, base_r=base_r, link_every=link_every)
    console.print(f"[green]Wrote[/green] {out}")


@app.command("map-eq")
def cmd_map_eq(
    path: str = typer.Argument(..., help="Path to a Tanakh JSON file."),
    equation: str = typer.Option(..., "--eq", help="Equation string, e.g. 'E=mc^2' or 'S_q=(1-sum p^q)/(q-1)'"),
    book: str = typer.Option(None, "--book", "-b", help="Restrict to a specific book."),
    top_k: int = typer.Option(10, "--top", help="How many matches to show."),
    window: int = typer.Option(40, "--window", help="Tokens per passage window."),
):
    """
    Experimental: maps an equation into a feature vector and searches for matching passages.
    This is NOT 'proof of encoded physics'—it's a structured similarity search.
    """
    doc = load_json(path)
    results = map_equation_to_passages(doc, equation=equation, restrict_book=book, window=window, top_k=top_k)

    table = Table(title=f"Equation map: {equation}")
    table.add_column("Rank", justify="right")
    table.add_column("Book")
    table.add_column("Start Ref")
    table.add_column("Score", justify="right")
    table.add_column("Preview")
    for i, r in enumerate(results, start=1):
        table.add_row(str(i), r["book"], r["start_ref"], f"{r['score']:.4f}", r["preview"])
    console.print(table)


if __name__ == "__main__":
    app()
