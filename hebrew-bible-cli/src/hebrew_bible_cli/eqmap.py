from __future__ import annotations

import heapq
import re
from typing import Any

import numpy as np

from .io import list_books, flatten_tokens
from .features import trope_intensity


# Matches identifiers (with underscores), decimal numbers, operators, and
# individual Greek/special math symbols (including ℏ and ∂).
EQ_TOKEN_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9_]*"
    r"|\d+(?:\.\d+)?"
    r"|[+\-*/^=()]"
    r"|[ℏ∂∫]"
    r"|[\u0370-\u03FF]"  # Greek and Coptic block
)

# -------------------------------------------------------------------
# LaTeX normalization
# -------------------------------------------------------------------

# Decorated-argument forms: \hat{X} -> Xhat,  \tilde{X} -> Xtilde, etc.
_DECORATED_RE = re.compile(r"\\(hat|tilde|bar|vec|dot|ddot|check|acute|grave|breve)\{([^}]+)\}")

# Named commands mapped to either a unicode symbol or a plain token.
_LATEX_NAMED: dict[str, str] = {
    r"\hbar": "ℏ",
    r"\partial": "∂",
    r"\nabla": "nabla",
    r"\infty": "infty",
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ε",
    r"\varepsilon": "ε",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\pi": "π",
    r"\rho": "ρ",
    r"\sigma": "σ",
    r"\tau": "τ",
    r"\upsilon": "υ",
    r"\phi": "φ",
    r"\varphi": "φ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    r"\Gamma": "Γ",
    r"\Delta": "Δ",
    r"\Theta": "Θ",
    r"\Lambda": "Λ",
    r"\Xi": "Ξ",
    r"\Pi": "Π",
    r"\Sigma": "Σ",
    r"\Upsilon": "Υ",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Omega": "Ω",
    r"\cdot": "*",
    r"\times": "*",
    r"\sum": "Σ",
    r"\prod": "Π",
    r"\frac": "/",
    r"\sqrt": "sqrt",
    r"\int": "∫",
}

# Sort longest key first so that e.g. \varepsilon is replaced before \var.
_LATEX_NAMED_SORTED = sorted(_LATEX_NAMED.items(), key=lambda kv: -len(kv[0]))


def normalize_latex(eq: str) -> str:
    """Normalize LaTeX math notation to plain tokens that EQ_TOKEN_RE can parse.

    Decorated-argument commands are rewritten so that the argument comes first
    and the decoration name is appended (e.g. ``\\hat{H}`` → ``Hhat``).
    Named commands are replaced by their Unicode equivalents or ASCII aliases
    (e.g. ``\\hbar`` → ``ℏ``, ``\\partial`` → ``∂``).

    Examples
    --------
    >>> normalize_latex(r"\\hat{H}")
    'Hhat'
    >>> normalize_latex(r"\\hbar")
    'ℏ'
    >>> normalize_latex(r"\\partial")
    '∂'
    """
    # 1. Decorated-argument forms: \hat{H} -> Hhat
    eq = _DECORATED_RE.sub(lambda m: m.group(2) + m.group(1), eq)
    # 2. Structured forms: \frac{a}{b} -> a/b
    eq = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"\1/\2", eq)
    # 3. Structured forms: \sqrt{x} -> sqrt(x)
    eq = re.sub(r"\\sqrt\{([^}]+)\}", r"sqrt(\1)", eq)
    # 4. Named commands (longest match first)
    for latex, plain in _LATEX_NAMED_SORTED:
        eq = eq.replace(latex, plain)
    eq = eq.replace("\\", "").replace("{", "").replace("}", "")
    return eq


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


_GREEK_RE = re.compile(r"^(?:[\u0370-\u03FF]|[ℏ∂∫])$")


class CounterLike(dict):
    def __missing__(self, key) -> int:
        return 0

    def total_unique(self) -> int:
        return len(self.keys())


def equation_vector(eq: str) -> np.ndarray:
    """Very simple equation embedding.

    - operator counts
    - Greek/special symbol counts (including ℏ and ∂)
    - decimal-number token counts
    - unique variable-name counts

    The input is first passed through :func:`normalize_latex` so that both
    plain-ASCII and LaTeX-style equations produce consistent feature vectors.
    This is intentionally conservative; swap in sympy + learned embeddings later.
    """
    tokens = EQ_TOKEN_RE.findall(normalize_latex(eq))
    ops = {"+": 0, "-": 0, "*": 0, "/": 0, "^": 0, "=": 0, "(": 0, ")": 0}
    greek: CounterLike = CounterLike()
    vars_: CounterLike = CounterLike()
    digits = 0

    for t in tokens:
        if t in ops:
            ops[t] += 1
        elif re.match(r"^\d", t):
            digits += 1
        elif _GREEK_RE.match(t):
            greek[t] += 1
        else:
            # variable names like E, m, c, S_q, Hhat, etc.
            vars_[t] += 1

    # Fixed feature order
    feat: list = []
    feat.extend([ops[k] for k in ["+", "-", "*", "/", "^", "=", "(", ")"]])
    # Greek/special symbols of interest
    for k in ["π", "φ", "ρ", "σ", "μ", "Σ", "Λ", "Δ", "Ψ", "ν", "χ", "λ", "τ", "ℏ", "∂"]:
        feat.append(greek[k])
    feat.append(digits)
    feat.append(len(tokens))
    feat.append(vars_.total_unique())
    return np.array(feat, dtype=float)


# Named indices into the equation feature vector produced by equation_vector().
# Layout: [8 ops][15 Greek: π φ ρ σ μ Σ Λ Δ Ψ ν χ λ τ ℏ ∂][digits][ntokens][nvars]
_EQ_IDX_PI    = 8   # π
_EQ_IDX_PHI   = 9   # φ
_EQ_IDX_RHO   = 10  # ρ
_EQ_IDX_SIGMA = 11  # σ
_EQ_IDX_MU    = 12  # μ
_EQ_IDX_SIGMA_CAP = 13  # Σ
_EQ_IDX_HBAR  = 21  # ℏ
_EQ_IDX_PARTIAL = 22  # ∂
_EQ_IDX_DIGITS  = 23  # decimal-number token count
_EQ_IDX_NVARS   = 25  # unique variable names


def passage_vector(tokens: list[dict]) -> np.ndarray:
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
    doc: dict[str, Any],
    equation: str,
    restrict_book: str | None = None,
    window: int = 40,
    top_k: int = 10
) -> list[dict[str, Any]]:
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
        eqv[0] + eqv[1],                                                        # +/- activity
        eqv[2] + eqv[3],                                                        # */ activity
        eqv[4],                                                                  # exponent
        eqv[5],                                                                  # equals
        eqv[_EQ_IDX_PI] + eqv[_EQ_IDX_PHI] + eqv[_EQ_IDX_RHO],               # π/φ/ρ group
        eqv[_EQ_IDX_SIGMA] + eqv[_EQ_IDX_MU] + eqv[_EQ_IDX_SIGMA_CAP]
        + eqv[_EQ_IDX_HBAR] + eqv[_EQ_IDX_PARTIAL],                           # σ/μ/Σ/ℏ/∂ group
        eqv[_EQ_IDX_DIGITS],                                                     # digits
        eqv[_EQ_IDX_NVARS],                                                      # unique vars
    ], dtype=float)

    if restrict_book:
        if restrict_book not in doc:
            raise KeyError(f"Book '{restrict_book}' not found. Available: {list_books(doc)}")
        books = [restrict_book]
    else:
        books = list_books(doc)

    # Use a fixed-size min-heap so memory stays O(top_k) instead of
    # accumulating all windows and sorting the entire list.
    heap: list[tuple[float, dict[str, Any]]] = []

    for book in books:
        # try chapters sequentially; if book structure differs, skip safely
        try:
            chapters = doc[book]["chapters"]
        except Exception:
            continue

        for chapter in sorted(chapters.keys(), key=lambda x: (0, int(x)) if str(x).isdigit() else (1, x)):
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

                entry = {
                    "book": book,
                    "start_ref": chunk[0]["ref"],
                    "score": score,
                    "preview": preview if preview else chunk[0]["ref"],
                }

                if len(heap) < top_k:
                    heapq.heappush(heap, (score, entry))
                elif score > heap[0][0]:
                    heapq.heapreplace(heap, (score, entry))

    return [item for _, item in sorted(heap, key=lambda x: x[0], reverse=True)]
