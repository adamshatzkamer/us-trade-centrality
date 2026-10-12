"""
Rank stability 2017 -> 2022, the pre-registered H1 forecast drawn as data.

Two panels: each state's trade prestige (in-flow eigenvector) rank and bridge
position (betweenness) rank in 2017 against 2022. Ranks use the average method,
so the plotted positions are exactly the ranks Spearman's rho is computed on;
the rho printed on each panel is recomputed here and checked against the
registered report (evolution_20260808_093628: 0.985 and 0.742). States with
zero betweenness share one tied rank and are drawn as a single labelled group.

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
REGISTERED = {"eigenvector": 0.985, "betweenness": 0.742}
PANELS = [
    ("eigenvector", "Trade prestige", "#009e73", "Hubs held"),
    ("betweenness", "Bridge position", "#0072b2", "Bridges moved"),
]
LABEL = {
    "eigenvector": ["TX", "KY", "MS", "DC"],
    "betweenness": ["MA", "MN"],
}
INK, MUTED, GRID = "#1f2a24", "#5a5c5b", "#e3e8e5"


def font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("IBM Plex Sans", "Helvetica Neue", "Helvetica", "Arial"):
        if name in names:
            return name
    return "sans-serif"


def load(year):
    with open(CACHE / f"cfs_{year}_full.pkl", "rb") as f:
        return pickle.load(f)["centralities"].set_index("label")


def panel(ax, df, key, title, color, verdict):
    a, b = df[f"{key}_2017"], df[f"{key}_2022"]
    rho = spearmanr(a, b).correlation
    assert round(rho, 3) == REGISTERED[key], (key, rho)
    ra = a.rank(ascending=False, method="average")
    rb = b.rank(ascending=False, method="average")

    ax.plot([1, 51], [1, 51], color=GRID, lw=2.5, zorder=1)
    zero = (a == 0) & (b == 0)
    ax.scatter(
        ra[~zero],
        rb[~zero],
        s=150,
        color=color,
        alpha=0.85,
        edgecolor="white",
        linewidth=1.2,
        zorder=3,
    )
    if zero.any():
        x, y = ra[zero].iloc[0], rb[zero].iloc[0]
        ax.scatter([x], [y], s=1400, facecolor="white", edgecolor=color, linewidth=2.5, zorder=2)
        ax.annotate(
            f"{int(zero.sum())} states with no brokerage\nin either year (tied)",
            (x, y),
            xytext=(x - 3, y + 9),
            fontsize=19,
            color=MUTED,
            ha="right",
            va="bottom",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2),
        )
    only17 = (a > 0) & (b == 0)
    only22 = (a == 0) & (b > 0)
    if only22.any():
        x = ra[only22].iloc[0]
        ax.text(
            x + 1.8,
            rb[only22].min() - 0.5,
            f"{int(only22.sum())} brokers\nin 2022 only",
            fontsize=17,
            color=MUTED,
            va="top",
        )
    if only17.any():
        names = ", ".join(sorted(ra[only17].index))
        ax.text(
            ra[only17].min() - 0.5,
            rb[only17].iloc[0] - 1.8,
            f"Brokers only in 2017:\n{names}",
            fontsize=17,
            color=MUTED,
            va="bottom",
        )
    for s in LABEL[key]:
        if s in ra.index and not zero.get(s, False):
            ax.annotate(
                s,
                (ra[s], rb[s]),
                xytext=(9, -6),
                textcoords="offset points",
                fontsize=20,
                fontweight="bold",
                color=INK,
                zorder=4,
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
    ax.set_xlabel("Rank in 2017", fontsize=20, color=MUTED, labelpad=12)
    ax.set_ylabel("Rank in 2022", fontsize=20, color=MUTED, labelpad=12)
    ax.text(
        0,
        1.13,
        title,
        transform=ax.transAxes,
        fontsize=30,
        fontweight="bold",
        color=INK,
        va="bottom",
    )
    ax.text(
        0,
        1.04,
        f"{verdict}: ρ = {rho:.3f}",
        transform=ax.transAxes,
        fontsize=24,
        color=color,
        fontweight="bold",
        va="bottom",
    )
    return rho


def main():
    c17, c22 = load(2017), load(2022)
    df = c17[["eigenvector", "betweenness"]].join(
        c22[["eigenvector", "betweenness"]], lsuffix="_2017", rsuffix="_2022", how="inner"
    )
    assert len(df) == 51, len(df)
    plt.rcParams["font.family"] = font()
    fig, axes = plt.subplots(1, 2, figsize=(16, 8.8), dpi=200)
    fig.patch.set_facecolor("white")
    for ax, (key, title, color, verdict) in zip(axes, PANELS):
        rho = panel(ax, df, key, title, color, verdict)
        print(f"{key}: rho = {rho:.4f}")
    fig.text(
        0.5,
        0.015,
        "Rank 1 at the top left. Dots on the diagonal kept their rank. "
        "Commodity Flow Survey 2017 and 2022, 50 states and DC.",
        ha="center",
        fontsize=17,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.15, wspace=0.22)
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"rank-stability-2017-2022.{ext}", facecolor="white")
    print("wrote", OUT / "rank-stability-2017-2022.png")


if __name__ == "__main__":
    main()
