# Measuring Structural Power in U.S. Interstate Commerce

GDP is how we rank state economies. But GDP tells you nothing about structural position — which states sit on critical trade routes, which ones draw heavily from well-connected suppliers, which ones are essential to the network even though their output is modest. This project applies network centrality to the 2017 Commodity Flow Survey to find out. 40% of states diverge significantly from their GDP rankings. Florida, the 4th largest economy, lies on zero shortest trade paths.

Master's thesis, Department of Systems Science and Industrial Engineering, Binghamton University.

## See It Live

- **[The Interstate Power Observatory](https://ustradeflow.systems/)** is the interactive dashboard: a hand-built SVG map of state centrality. Filter by commodity, toggle domestic vs. international, click a state for its trade profile, and deep-link any view (`?state=TX&measure=betweenness`). Source and design system live in [`web/`](web/) (React + TypeScript; see [`web/DESIGN.md`](web/DESIGN.md)). The earlier Plotly dashboard at `us-trade.plotly.app` is kept as an archive.
- **Pre-rendered notebooks** — browse results without installing anything:
  - [`companion.html`](notebooks/__marimo__/companion.html) — full exploratory analysis
  - [`replication.html`](notebooks/__marimo__/replication.html) — static replication of thesis figures

## Key Findings

Three centrality measures applied to a 51-node interstate trade network (50 states + DC, 2,534 edges, 99.4% density):

- **40% of states diverge ≥5 rank positions** between GDP and eigenvector centrality. The pattern tracks industry composition: manufacturing and energy states overperform, service economies underperform.
- **Betweenness centrality reshuffles under boundary change** (ρ = 0.816 when international trade is added) while eigenvector and out-degree remain stable (ρ > 0.98). Boundary specification is not a trivial methodological choice.
- **All measures survive 33% graph filtration** with ρ = 1.000. Rankings are driven by the high-value trade backbone, not low-weight noise.

## Corrections

- **Eigenvector direction (October 2026).** Thesis Equation 3.2 writes the out-flow eigenvector; every reported value is the in-flow version (NetworkX's default on a directed graph). The numbers are correct for the in-flow version, and six of the eight structurally undervalued states hold under either direction; Louisiana and Montana do not. Details and the full comparison: [`paper/ERRATA.md`](paper/ERRATA.md).
- **Which states are structurally undervalued (October 2026).** The thesis lists eight states without stating the rule; North Dakota ties three of them at +6 and is omitted. Corrected definition: eigenvector rank at least 5 places above GDP rank, which gives 11 states in 2017. See [`paper/ERRATA.md`](paper/ERRATA.md) §2.

## Explore the Data

Three [Marimo](https://marimo.io) notebooks for interactive exploration:

```bash
marimo edit notebooks/companion.py          # 5-act exploratory analysis
marimo edit notebooks/prenormalization.py    # GDP pre-normalization sensitivity test
marimo edit notebooks/defense.py            # Compact defense Q&A notebook
```

`companion.py` is the main notebook — edge weight distributions, choropleths, filtration sweeps, boundary sensitivity comparisons. `prenormalization.py` tests whether rankings change when edge weights are normalized by GDP before computing centrality (they don't — eigenvector ρ = 0.980). `defense.py` is a streamlined 6-cell version for live presentation.

## Custom Analysis

The toolkit supports asking your own questions. The pattern: **load → transform → compute → compare**.

```python
import pandas as pd
from cfs_toolkit.analysis import load_network_graph
from cfs_toolkit.core import compute_all_centralities
from cfs_toolkit.core.normalizations import gdp_sender, gdp_geometric

# Load the pre-built network (no raw data needed)
G = load_network_graph("results/51x51_domestic")
gdp = pd.read_csv("data/state_gdp_2017.csv")

# Transform edge weights (your research question)
G_norm = gdp_sender(G, gdp)  # or gdp_geometric(G, gdp), or your own function

# Compute centralities on the transformed network
df = compute_all_centralities(G_norm)
```

Any function that takes a `nx.DiGraph` and returns a new `nx.DiGraph` with modified `weight` edge attributes will work with `compute_all_centralities()`. See `notebooks/prenormalization.py` for a complete worked example.

## Reproducing Results

**Canonical results are included** in `results/` — you can explore them immediately without running the pipeline or downloading raw data.

**To regenerate from scratch:**

```bash
# 1. Set up environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e cfs-network-toolkit/

# 2. Obtain data (see data/README.md for download instructions)
python scripts/setup_data.py

# 3. Run the pipeline
python main.py                 # 51×51 domestic network (default)
python main.py --international # 52×52 with Rest of World node

# 4. Generate publication figures
python -m cfs_toolkit.figures results/51x51_domestic/

# 5. Validate
python tests/validate_pipeline.py
```

## Data

The pipeline requires the **CFS 2017 Public Use File** (~477 MB, 5,978,523 records) from the U.S. Census Bureau. This file cannot be redistributed. See [`data/README.md`](data/README.md) for download instructions.

The **FAF 5.7.1** dataset (~504 MB) is needed only for the 52×52 international network.

## Repository Structure

```
us-trade-centrality/
├── main.py                    # Pipeline entry point
├── configs/                   # YAML pipeline configurations
│   ├── domestic.yaml          #   51×51 (default)
│   ├── international.yaml     #   52×52 with RoW
│   └── filtered_33pct.yaml    #   33% edge filtration
├── cfs-network-toolkit/       # Pip-installable analysis library
│   └── cfs_toolkit/
│       ├── core/              #   Pipeline: load → preprocess → build → centralities
│       ├── analysis/          #   Filtration, boundary sensitivity, GDP comparison
│       ├── figures/           #   Static figure generation
│       ├── visualizations/    #   Publication-ready charts
│       └── commands/          #   CLI interface (cfs <command>)
├── data/                      # Data directory (see data/README.md)
├── results/                   # Canonical pipeline outputs
│   ├── 51x51_domestic/        #   Domestic network results
│   ├── 52x52_international/   #   International network results
│   ├── normalization_comparison/ # Pre-normalization sensitivity results
│   └── commodity_analysis/    #   Per-SCTG commodity analysis
├── notebooks/                 # Marimo interactive notebooks
│   ├── companion.py           #   5-act interactive exploration
│   ├── prenormalization.py    #   Pre-normalization sensitivity analysis
│   ├── defense.py             #   Compact defense notebook
│   ├── replication.py         #   Static replication notebook
│   └── __marimo__/            #   Pre-rendered HTML exports
├── paper/                     # Thesis LaTeX and figures
│   ├── figures/               #   All publication figures (PNG + PDF)
│   └── references.bib
├── scripts/                   # Standalone utilities (incl. export_viz_data.py → web/public/data)
├── tests/
│   ├── validate_pipeline.py   # End-to-end pipeline validation
│   └── test_export_schema.py  # Web data-contract schema check (zero gated data)
├── web/                       # The Interstate Power Observatory (React + TS; see web/DESIGN.md)
├── evolution/                 # Three-survey study (2012/2017/2022) — see note below
└── viz/                       # Interactive Dash app (archived; still the CSV source for web export)
```

> **`evolution/` is frozen.** It holds a ResearchHub pre-registration whose `thresholds.yaml`
> hash is published. Do not modify or re-run anything under `evolution/` outside a deliberate
> post-registration run. CI is scoped to skip it.

## Citation

Thesis citation and DOI will be added upon publication.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
