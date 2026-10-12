"""
Trade prestige held on both arcs of the registered evolution study.

Two panels of each state's trade prestige (in-flow eigenvector) rank: 2017
against 2012 (the retrodiction arc, before COVID, the control) and 2017 against
2022 (the prediction arc, through COVID). Rho and the top-10 overlap are
recomputed from the evolution cache and asserted against the registered report
(evolution_20260808_093628: 0.988 and 0.985; 9 of 10 on both arcs).

Reads the frozen evolution cache read-only; writes figures/ here.
"""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
CACHE = HERE.parents[1] / "evolution" / "cache"
OUT = HERE / "figures"
REGISTERED = {2012: 0.988, 2022: 0.985}
ARCS = [
    (2012, "2017 vs 2012: before COVID", "#7fbfa9"),
    (2022, "2017 vs 2022: through COVID", "#009e73"),
]
LABEL = ["TX", "KY", "MS", "DC"]
INK, MUTED, GRID = "#1f2a24", "#5a5c5b", "#e3e8e5"


def font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("IBM Plex Sans", "Helvetica Neue", "Helvetica", "Arial"):
        if name in names:
            return name
    return "sans-serif"


def load(year):
    with open(CACHE / f"cfs_{year}_full.pkl", "rb") as f:
        return pickle.load(f)["centralities"].set_index("label")["eigenvector"]


def panel(ax, base, other, year, title, color):
    other = other.reindex(base.index)
    rho = spearmanr(base, other).correlation
    assert round(rho, 3) == REGISTERED[year], (year, rho)
    r0 = base.rank(ascending=False, method="average")
    r1 = other.rank(ascending=False, method="average")
    top = len(set(r0[r0 <= 10].index) & set(r1[r1 <= 10].index))
    assert top == 9, (year, top)

    ax.plot([1, 51], [1, 51], color=GRID, lw=2.5, zorder=1)
    ax.scatter(r0, r1, s=170, color=color, edgecolor="white", linewidth=1.3, zorder=2)
    for s in LABEL:
        ax.annotate(
            s,
            (r0[s], r1[s]),
            xytext=(11, -7),
            textcoords="offset points",
            fontsize=20,
            fontweight="bold",
            color=INK,
        )
    ax.set_xlim(-1, 53)
    ax.set_ylim(53, -1)
    ticks = [1, 10, 20, 30, 40, 51]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.tick_params(labelsize=18, colors=MUTED, length=0, pad=8)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.grid(color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_aspect("equal")
    ax.set_xlabel("Trade prestige rank in 2017", fontsize=20, color=MUTED, labelpad=12)
    ax.set_ylabel(f"Rank in {year}", fontsize=20, color=MUTED, labelpad=12)
    ax.text(
        0,
        1.13,
        title,
        transform=ax.transAxes,
        fontsize=28,
        fontweight="bold",
        color=INK,
        va="bottom",
    )
    ax.text(
        0,
        1.04,
        f"Rank correlation {rho:.3f} · {top} of top 10 kept",
        transform=ax.transAxes,
        fontsize=23,
        color=color if year == 2022 else "#3f8f75",
        fontweight="bold",
        va="bottom",
    )
    return rho


def main():
    base = load(2017)
    assert len(base) == 51
    plt.rcParams["font.family"] = font()
    fig, axes = plt.subplots(1, 2, figsize=(16, 8.8), dpi=200)
    fig.patch.set_facecolor("white")
    for ax, (year, title, color) in zip(axes, ARCS):
        rho = panel(ax, base, load(year), year, title, color)
        print(f"2017 vs {year}: rho = {rho:.4f}")
    fig.text(
        0.5,
        0.015,
        "Rank 1 at the top left. Dots on the diagonal kept their rank. "
        "Commodity Flow Survey 2012, 2017 and 2022, 50 states and DC.",
        ha="center",
        fontsize=17,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.15, wspace=0.22)
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"prestige-both-arcs.{ext}", facecolor="white")
    print("wrote", OUT / "prestige-both-arcs.png")


if __name__ == "__main__":
    main()
