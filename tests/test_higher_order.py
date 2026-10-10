"""Tests for the post-hoc higher-order study (analysis/higher_order/).

Each measure gets a case it must pass and a case it must fail, so a measure that
cannot fail would show up here.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np

HO_DIR = Path(__file__).resolve().parent.parent / "analysis" / "higher_order"
sys.path.insert(0, str(HO_DIR))


def load(name):
    spec = importlib.util.spec_from_file_location(name, HO_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


three_way = load("run_three_way")
states_as_variables = load("run_states_as_variables")


def synthetic(rng, n=6, c=4):
    band = rng.integers(0, 3, (n, n))
    band[np.arange(n), np.arange(n)] = -1
    offdiag = (band >= 0)[..., None]
    base = (
        rng.gamma(2, 1, (n, n, 1))
        * rng.gamma(2, 1, (n, 1, c))
        * rng.gamma(2, 1, (1, n, c))
        * offdiag
    )
    return band, base, offdiag


def test_pairs_model_is_exact_without_three_way_structure():
    band, base, _ = synthetic(np.random.default_rng(0))
    p = base / base.sum()
    assert three_way.kl(p, three_way.fit_pairs(p)) < 1e-9


def test_distance_term_removes_a_band_by_commodity_effect():
    rng = np.random.default_rng(1)
    band, base, offdiag = synthetic(rng)
    effect = np.exp(rng.normal(0, 1, (3, 4)))[np.where(band >= 0, band, 0)] * offdiag
    p = base * effect / (base * effect).sum()
    assert three_way.kl(p, three_way.fit_pairs(p)) > 0.01
    assert three_way.kl(p, three_way.fit_pairs(p, band)) < 1e-6


def test_distance_term_leaves_unrelated_three_way_structure():
    rng = np.random.default_rng(2)
    band, base, offdiag = synthetic(rng)
    t = base * np.exp(rng.normal(0, 1, base.shape)) * offdiag
    p = t / t.sum()
    assert three_way.kl(p, three_way.fit_pairs(p, band)) > 0.5 * three_way.kl(
        p, three_way.fit_pairs(p)
    )


def test_o_information_signs():
    rng = np.random.default_rng(3)
    x = rng.normal(size=(20000, 2))
    total = x.sum(1) + 0.3 * rng.normal(size=20000)
    common = rng.normal(size=20000)
    copies = np.column_stack([common + 0.3 * rng.normal(size=20000) for _ in range(3)])
    independent = rng.normal(size=(20000, 3))
    oi = states_as_variables.o_information
    assert oi(np.corrcoef(np.column_stack([x, total]).T)) < -0.5
    assert oi(np.corrcoef(copies.T)) > 0.5
    assert abs(oi(np.corrcoef(independent.T))) < 0.01


dependence = load("run_dependence")


def test_sole_supplier_link_needs_a_majority():
    import pandas as pd

    cells = pd.DataFrame(
        {
            "d": ["X", "X", "Y", "Y", "Y"],
            "SCTG": ["02"] * 5,
            "o": ["A", "B", "A", "B", "C"],
            "usd": [60.0, 40.0, 40.0, 35.0, 25.0],
            "records": [6, 4, 4, 3, 2],
        }
    )
    links = dependence.sole_supplier_links(cells)
    assert list(zip(links.d, links.o)) == [("X", "A")]
    assert links.records.tolist() == [6] and links.dc_records.tolist() == [10]


def test_mode_groups_reject_unknown_codes():
    import pandas as pd
    import pytest

    assert dependence.mode_group(2022, pd.Series([111, 21, 15])).tolist() == [
        "truck",
        "air/parcel",
        "pipeline",
    ]
    assert dependence.mode_group(2017, pd.Series([4, 14, 12])).tolist() == [
        "truck",
        "air/parcel",
        "pipeline",
    ]
    with pytest.raises(KeyError):
        dependence.mode_group(2022, pd.Series([4]))


def test_hhi_bounds():
    import pandas as pd

    w = pd.Series([1.0, 1.0, 1.0, 1.0, 5.0])
    keys = pd.Series(["even"] * 4 + ["single"])
    h = dependence.hhi(w, keys)
    assert abs(h["even"] - 0.25) < 1e-12 and h["single"] == 1.0


def test_groups_without_three_way_structure_pool_into_some():
    rng = np.random.default_rng(4)
    _, a, _ = synthetic(rng)
    _, b, _ = synthetic(rng)
    for t in (a, b):
        assert three_way.kl(t / t.sum(), three_way.fit_pairs(t / t.sum())) < 1e-9
    pooled_t = a + b
    pooled = three_way.cell_terms(
        pooled_t / pooled_t.sum(), three_way.fit_pairs(pooled_t / pooled_t.sum())
    )
    assert pooled.sum() > 0.01
    shares = [dependence.attributed_share(pooled, pooled_t, t) for t in (a, b)]
    assert abs(sum(shares) - 1) < 1e-9
    _, c, offdiag = synthetic(rng)
    c = c * np.exp(rng.normal(0, 1, c.shape)) * offdiag
    assert three_way.kl(c / c.sum(), three_way.fit_pairs(c / c.sum())) > 0.01


equivalence = load("run_equivalence")


def test_ipf_and_poisson_regression_give_the_same_fit():
    rng = np.random.default_rng(4)
    n = rng.poisson(rng.gamma(2, 20, (4, 5, 3))).astype(float)
    n[0, 1, :] = 0  # a zero margin puts the estimate on the boundary
    pairs = [(0, 1), (0, 2), (1, 2)]
    r = equivalence.compare(n, pairs)
    assert r["max_abs_difference"] < 1e-6
    assert abs(r["two_n_ln2_loss"] - r["poisson_deviance"]) < 1e-6 * r["poisson_deviance"]


def test_different_margins_give_different_fits():
    rng = np.random.default_rng(5)
    n = rng.poisson(rng.gamma(2, 20, (4, 5, 3))).astype(float)
    pairs = [(0, 1), (0, 2), (1, 2)]
    independence = [(0,), (1,), (2,)]
    mu, _ = equivalence.poisson_fit(n, independence)
    assert np.abs(equivalence.ipf(n, pairs) - mu).max() > 1


replaceability = load("run_replaceability")


def replaceability_case(alt_supply, alt_miles):
    """NH buys 100 of SCTG 02, all from MA over 100 miles; ME ships alt_supply of 02 to
    VT, and ME's shipments to NH have a median of alt_miles."""
    import pandas as pd

    cells = pd.DataFrame({
        "o": ["MA", "ME"], "d": ["NH", "VT"], "SCTG": ["02", "02"],
        "usd": [100.0, alt_supply], "dist": [100.0, 80.0],
    })
    pairs = pd.DataFrame({"o": ["MA", "ME", "ME"], "d": ["NH", "VT", "NH"],
                          "dist": [100.0, 80.0, alt_miles]})
    links = pd.DataFrame({"d": ["NH"], "SCTG": ["02"], "o": ["MA"], "usd": [100.0],
                          "r": [100.0]})
    return replaceability.candidates(links, cells, pairs, ["MA", "ME", "NH", "VT"])


def test_an_obvious_alternative_is_counted():
    cand = replaceability_case(alt_supply=500.0, alt_miles=90.0)
    assert set(cand.alt) == {"ME", "VT"}
    for k in replaceability.KS:
        assert replaceability.count_alternatives(cand, k, 0).tolist() == [1]


def test_no_alternative_without_volume():
    import pandas as pd

    cand = replaceability_case(alt_supply=50.0, alt_miles=90.0)
    for k in replaceability.KS:
        for delta in replaceability.DELTAS:
            assert replaceability.count_alternatives(cand, k, delta).tolist() == [0]
    classes = replaceability.classify(pd.Series([0, 2, 3])).tolist()
    assert classes == ["none", "thin", "replaceable"]


def test_a_far_alternative_needs_a_looser_distance_bound():
    cand = replaceability_case(alt_supply=500.0, alt_miles=150.0)
    assert replaceability.count_alternatives(cand, 1, 0).tolist() == [0]
    assert replaceability.count_alternatives(cand, 1, 1).tolist() == [1]
    assert abs(replaceability.delta_needed(cand, 1).iloc[0] - 0.5) < 1e-12
    vt = cand[cand.alt == "VT"].iloc[0]
    assert vt.dist_source == "centroid" and 0 < vt.alt_dist < 100


identify = load("run_identify_state")


def test_unique_count_separates_distinct_from_shared_profiles():
    distinct = np.array([[3.0, 2, 1], [1, 3, 2], [2, 1, 3]])
    shared = np.array([[3.0, 2, 1], [3, 2, 1], [3, 2, 1]])
    zeros = np.zeros((3, 3))
    assert identify.unique_count(distinct, zeros, 1) == 3
    assert identify.unique_count(shared, zeros, 1) == 0
    assert identify.unique_count(shared, distinct, 1) == 3
