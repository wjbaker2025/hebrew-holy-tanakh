from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt

from .features import trope_intensity


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def build_double_helix(tokens: List[dict], pitch: float = 0.09, base_r: float = 1.0):
    """
    Strand A: semantic anchor (Strong's + morphology hash)
    Strand B: musical/prosodic (trope intensity)
    """
    strong_vals = np.array([_safe_int(t["strongs"]) for t in tokens], dtype=float)
    if strong_vals.size == 0:
        strong_vals = np.array([0.0])

    s_min, s_max = float(strong_vals.min()), float(strong_vals.max())
    s_span = max(1.0, s_max - s_min)

    trope_vals = np.array([trope_intensity(t["hebrew"]) for t in tokens], dtype=float)
    t_min, t_max = float(trope_vals.min()), float(trope_vals.max())
    t_span = max(1e-9, t_max - t_min)

    A = {"x": [], "y": [], "z": []}
    B = {"x": [], "y": [], "z": []}

    t_param = 0.0
    dt_base = 0.6

    for i, tok in enumerate(tokens):
        s_norm = (_safe_int(tok["strongs"]) - s_min) / s_span
        ti = trope_intensity(tok["hebrew"])
        ti_norm = (ti - t_min) / t_span

        # radii (tunable)
        rA = base_r * (0.85 + 0.30 * s_norm)
        rB = base_r * (0.85 + 0.30 * ti_norm)

        # time dilation by prosody (cadence)
        dt = dt_base * (1.0 + 0.35 * ti_norm)

        xA = rA * math.cos(t_param)
        yA = rA * math.sin(t_param)
        z = pitch * t_param

        xB = rB * math.cos(t_param + math.pi)
        yB = rB * math.sin(t_param + math.pi)
        zB = z

        A["x"].append(xA); A["y"].append(yA); A["z"].append(z)
        B["x"].append(xB); B["y"].append(yB); B["z"].append(zB)

        t_param += dt

    return A, B


def render_helix_png(tokens: List[dict], out_path: str, pitch: float = 0.09, base_r: float = 1.0, link_every: int = 1):
    A, B = build_double_helix(tokens, pitch=pitch, base_r=base_r)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(A["x"], A["y"], A["z"])
    ax.plot(B["x"], B["y"], B["z"])

    for i in range(0, len(A["x"]), max(1, link_every)):
        ax.plot([A["x"][i], B["x"][i]],
                [A["y"][i], B["y"][i]],
                [A["z"][i], B["z"][i]])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close(fig)
