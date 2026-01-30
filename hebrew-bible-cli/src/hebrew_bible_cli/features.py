from __future__ import annotations

import regex as re
from typing import List, Dict

# Hebrew cantillation marks (te'amim) generally U+0591..U+05AF
CANT_RE = re.compile(r"[\u0591-\u05AF]")
METEG_RE = re.compile(r"[\u05BD]")  # meteg
MAQAF = "־"
SOF_PASUQ = "׃"
PASEQ = "׀"


def trope_intensity(hebrew: str) -> float:
    cant = len(CANT_RE.findall(hebrew))
    meteg = 1 if METEG_RE.search(hebrew) else 0
    punc = 1 if (SOF_PASUQ in hebrew or PASEQ in hebrew or "!" in hebrew) else 0
    maqaf = 1 if (MAQAF in hebrew) else 0
    # Tunable weights
    return cant + 0.5 * meteg + 0.5 * punc + 0.2 * maqaf


def trope_stats_for_tokens(tokens: List[dict]) -> Dict[str, float]:
    intensities = [trope_intensity(t["hebrew"]) for t in tokens]
    cant_count = sum(len(CANT_RE.findall(t["hebrew"])) for t in tokens)
    meteg_count = sum(1 for t in tokens if METEG_RE.search(t["hebrew"]))
    sof_count = sum(1 for t in tokens if SOF_PASUQ in t["hebrew"])
    paseq_count = sum(1 for t in tokens if PASEQ in t["hebrew"])
    maqaf_count = sum(1 for t in tokens if MAQAF in t["hebrew"])

    n = max(1, len(tokens))
    return {
        "tokens": len(tokens),
        "cantillation_marks_total": cant_count,
        "cantillation_marks_per_token": cant_count / n,
        "meteg_tokens": meteg_count,
        "sof_pasuq_tokens": sof_count,
        "paseq_tokens": paseq_count,
        "maqaf_tokens": maqaf_count,
        "avg_trope_intensity": sum(intensities) / n,
        "max_trope_intensity": max(intensities) if intensities else 0.0,
    }
