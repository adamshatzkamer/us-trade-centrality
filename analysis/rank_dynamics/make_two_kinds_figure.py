"""
Two kinds of network position, 2017: each state's trade prestige rank (in-flow
eigenvector) against its bridge position rank (betweenness).

States with zero betweenness have no bridge rank (they share one tied rank in
the raw data), so they are drawn in a separate band below the chart, placed by
trade prestige alone. Reads the dashboard's published centralities
(web/public/data/centralities_51.json); writes figures/ here.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "web" / "public" / "data" / "centralities_51.json"
OUT = HERE / "figures"
INK, MUTED, GRID = "#1f2a24", "#5a5c5b", "#e3e8e5"
BRIDGE, NONE, FL_C, MA_C = "#8fbfe0", "#9fd6bf", "#009e73", "#0072b2"
NAMED = {"TX", "CA", "IL", "PA", "OH", "NY", "MN", "KY"}


def font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("IBM Plex Sans", "Helvetica Neue", "Helvetica", "Arial"):
        if name in names:
            return name
    return "sans-serif"


def main():
    rows = json.loads(DATA.read_text())
    assert len(rows) == 51
    brokers = [r for r in rows if r["betweenness"] > 0]
    none = [r for r in rows if r["betweenness"] == 0]
    plt.rcParams["font.family"] = font()
    fig, (ax, band) = plt.subplots(
        2, 1, figsize=(16, 8.6), dpi=200, gridspec_kw={"height_ratios": [5, 1.15], "hspace": 0.06}
    )
    fig.patch.set_facecolor("white")

    gmax = max(r["gdp_billions"] for r in rows)

    def size(r):
        return 90 + 1300 * (r["gdp_billions"] / gmax)

    def color(s, base):
        return FL_C if s == "FL" else MA_C if s == "MA" else base

    for r in brokers:
        s = r["state"]
        hl = s in ("FL", "MA")
        ax.scatter(
            r["rank_eigenvector"],
            r["rank_betweenness"],
            s=size(r),
            color=color(s, BRIDGE),
            edgecolor="white",
            linewidth=1.5,
            alpha=1 if hl else 0.9,
            zorder=3 if hl else 2,
        )
        if hl or s in NAMED:
            ax.annotate(
                s,
                (r["rank_eigenvector"], r["rank_betweenness"]),
                xytext=(-(size(r) ** 0.5 / 2 + 6) if s == "TX" else size(r) ** 0.5 / 2 + 6, -7),
                ha="right" if s == "TX" else "left",
                textcoords="offset points",
                fontsize=26 if hl else 19,
                fontweight="bold",
                color=color(s, INK) if hl else INK,
            )
    for r in none:
        s = r["state"]
        hl = s == "FL"
        band.scatter(
            r["rank_eigenvector"],
            0,
            s=size(r),
            color=color(s, NONE),
            edgecolor="white",
            linewidth=1.5,
            alpha=1 if hl else 0.9,
            zorder=3 if hl else 2,
        )
        if hl or s in NAMED:
            band.annotate(
                s,
                (r["rank_eigenvector"], 0),
                xytext=(0, 20),
                textcoords="offset points",
                ha="center",
                fontsize=26 if hl else 19,
                fontweight="bold",
                color=color(s, INK) if hl else INK,
            )

    n_b = len(brokers)
    ax.set_xlim(0, 52)
    ax.set_ylim(n_b + 1, 0)
    ax.set_xticks([])
    ax.set_yticks([1, 5, 10, 15, n_b])
    ax.set_ylabel(
        f"Bridge position rank\n({n_b} states broker)", fontsize=21, color=MUTED, labelpad=12
    )
    ax.text(
        51.5,
        1.2,
        "Strong bridges, weak hubs",
        ha="right",
        va="top",
        fontsize=20,
        color=MUTED,
        style="italic",
    )
    ax.text(51.5, n_b + 0.6, "Dot size: GDP", ha="right", va="bottom", fontsize=18, color=MUTED)

    band.set_xlim(0, 52)
    band.set_ylim(-0.7, 1.3)
    band.set_yticks([])
    band.set_xticks([1, 10, 20, 30, 40, 51])
    band.set_xlabel("Trade prestige rank (1 = highest)", fontsize=21, color=MUTED, labelpad=10)
    band.text(
        51.5,
        0.75,
        f"No brokerage: {len(none)} states",
        fontsize=19,
        color=MUTED,
        va="bottom",
        ha="right",
        style="italic",
    )
    for a in (ax, band):
        for side in a.spines.values():
            side.set_visible(False)
        a.grid(color=GRID, lw=1, axis="x")
        a.tick_params(labelsize=18, colors=MUTED, length=0, pad=8)
        a.set_axisbelow(True)
    ax.grid(color=GRID, lw=1, axis="y")
    band.set_facecolor("#f5f7f6")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.97, bottom=0.12)
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"two-kinds-of-position-2017.{ext}", facecolor="white")
    print(f"brokers {n_b}, no brokerage {len(none)}; wrote", OUT / "two-kinds-of-position-2017.png")


if __name__ == "__main__":
    main()
