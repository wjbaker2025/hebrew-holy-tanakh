from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .io import list_books, flatten_tokens
from .features import trope_intensity


EQ_TOKEN_RE = re.compile(r"[A-Za-z]+|\d+|[\+\-\*/\^\=\(\)]|[λτπφρσμΣΛΔΨνχ]")


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def equation_vector(eq: str) -> np.ndarray:
    """
    Very simple equation embedding:
    - operator counts
    - greek symbol counts
    - digit counts
    - variable token counts
    This is intentionally conservative; you can swap in sympy + learned embeddings later.
    """
    tokens = EQ_TOKEN_RE.findall(eq)
    ops = {"+": 0, "-": 0, "*": 0, "/": 0, "^": 0, "=": 0, "(": 0, ")": 0}
    greek = CounterLike()
    vars_ = CounterLike()
    digits = 0

    for t in tokens:
        if t in ops:
            ops[t] += 1
        elif t.isdigit():
            digits += 1
        elif re.fullmatch(r"[λτπφρσμΣΛΔΨνχ]", t):
            greek[t] += 1
        else:
            # variable names like E, m, c, S_q, etc.
            vars_[t] += 1

    # Fixed feature order
    feat = []
    feat.extend([ops[k] for k in ["+", "-", "*", "/", "^", "=", "(", ")"]])
    # Some greek symbols you care about
    for k in ["π", "φ", "ρ", "σ", "μ", "Σ", "Λ", "Δ", "Ψ", "ν", "χ", "λ", "τ"]:
        feat.append(greek[k])
    feat.append(digits)
    feat.append(len(tokens))
    feat.append(vars_.total_unique())
    return np.array(feat, dtype=float)


class CounterLike(dict):
    def __missing__(self, key):
        return 0
    def total_unique(self) -> int:
        return len(self.keys())


def passage_vector(tokens: List[dict]) -> np.ndarray:
    """
    Passage embedding:
    - Strong's range/variance proxies (semantic diversity)
    - prosody intensity mean/var (musical dynamics)
    - morphology diversity proxy
    """
    if not tokens:
        return np.zeros(8, dtype=float)

    strongs = np.array([_safe_int(t["strongs"]) for t in tokens], dtype=float)
    ti = np.array([trope_intensity(t["hebrew"]) for t in tokens], dtype=float)

    morph = [t.get("morphology", "") for t in tokens]
    morph_unique = len(set(morph))

    return np.array([
        float(strongs.mean()),
        float(strongs.std()),
        float(strongs.min()),
        float(strongs.max()),
        float(ti.mean()),
        float(ti.std()),
        float(ti.max()),
        float(morph_unique),
    ], dtype=float)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denom)


def map_equation_to_passages(
    doc: Dict[str, Any],
    equation: str,
    restrict_book: Optional[str] = None,
    window: int = 40,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Search over sliding windows of tokens, scoring similarity between:
    - equation vector (symbolic structure)
    - passage vector (semantic/prosodic structure)

    NOTE: Vectors differ in dimension; we match by projecting both into a shared small space.
    Here we do a cheap trick: we reduce equation features to 8 dims to match passage dims.
    Replace later with a shared embedding model.
    """
    eqv = equation_vector(equation)
    # crude projection to 8 dims (stable, deterministic)
    eqp = np.array([
        eqv[0] + eqv[1],       # +/- activity
        eqv[2] + eqv[3],       # */ activity
        eqv[4],                # exponent
        eqv[5],                # equals
        eqv[8] + eqv[9] + eqv[10],  # π/φ/ρ group
        eqv[11] + eqv[12] + eqv[13],# σ/μ/Σ group
        eqv[-3],               # digits
        eqv[-1],               # unique vars
    ], dtype=float)

    books = [restrict_book] if restrict_book else list_books(doc)
    results = []

    for book in books:
        # try chapters sequentially; if book structure differs, skip safely
        try:
            chapters = doc[book]["chapters"]
        except Exception:
            continue

        for chapter in sorted(chapters.keys(), key=lambda x: int(x) if str(x).isdigit() else x):
            toks = flatten_tokens(doc, book=book, chapter=chapter)
            if len(toks) < window:
                continue

            for start in range(0, len(toks) - window + 1, max(1, window // 4)):
                chunk = toks[start:start + window]
                pv = passage_vector(chunk)

                # normalize scales a bit
                pv_norm = np.array([
                    pv[0] / 10000.0,
                    pv[1] / 1000.0,
                    pv[2] / 10000.0,
                    pv[3] / 10000.0,
                    pv[4],
                    pv[5],
                    pv[6],
                    pv[7] / 50.0
                ], dtype=float)

                score = cosine(eqp, pv_norm)
                preview = " ".join([c["english"] for c in chunk[:12] if c.get("english")])[:140]

                results.append({
                    "book": book,
                    "start_ref": chunk[0]["ref"],
                    "score": score,
                    "preview": preview if preview else chunk[0]["ref"],
                })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]
