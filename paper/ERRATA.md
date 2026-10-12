# Errata

Corrections to the master's thesis (*Testing Network Centrality for Economic
Power Measurement: Structure and Boundaries in U.S. Interstate Trade*,
Binghamton University, 2026) and the CCS 2026 abstract. The deposited texts are
not changed; this file records what is corrected and why.

## 1. Direction of the eigenvector centrality (October 2026)

**What the thesis says.** Equation 3.2 (p. 13) defines eigenvector centrality as

C_E(i) = (1/λ) Σ_j W_ij · C_E(j), with W_ij the flow from state i to state j.

This scores a state by the centrality of the states it ships *to* (the right
eigenvector of the origin-by-destination flow matrix, the out-flow version).

**What was computed.** Every eigenvector value in the thesis, the dashboard and
the follow-up study comes from NetworkX's `eigenvector_centrality_numpy` on the
directed network. For a directed graph, NetworkX returns the left eigenvector,
which scores a state by the centrality of the states that ship *to it* (the
in-flow version):

C_E(i) = (1/λ) Σ_j W_ji · C_E(j).

The reported numbers match the in-flow version exactly in all four networks
checked (thesis 2017, and the 2012, 2017 and 2022 study networks). The equation
and the computation disagree in direction; the numbers are correct for the
in-flow version.

**Corrected statement.** Equation 3.2 should read W_ji in place of W_ij. In
words: a state ranks high when it receives large shipments from states that
themselves rank high.

**Effect on results.** The two versions agree closely (Spearman ρ = 0.945 to
0.954 across the four networks), but 15 to 18 states move five or more ranks
between them. For 2017:

| | GDP rank | In-flow (reported) | Out-flow | Places above GDP, in / out |
|---|---|---|---|---|
| Kentucky | 28 | 14 | 15 | +14 / +13 |
| Mississippi | 37 | 27 | 28 | +10 / +9 |
| Indiana | 16 | 10 | 8 | +6 / +8 |
| Tennessee | 18 | 12 | 10 | +6 / +8 |
| Michigan | 14 | 8 | 9 | +6 / +5 |
| South Carolina | 26 | 19 | 19 | +7 / +7 |
| Louisiana | 24 | 17 | 25 | +7 / −1 |
| Montana | 49 | 41 | 48 | +8 / +1 |

Six of the eight structurally undervalued states the thesis discusses hold
under both versions. Louisiana and Montana are undervalued only under the in-flow
version reported. Other large differences: Florida 5th (in-flow) against 17th
(out-flow), Texas 1st against 5th.

**Interpretation.** Two sentences read the measure as the out-flow version: "a
state with high eigenvector centrality trades heavily with other economically
important states" (p. 13) and "Eigenvector centrality reveals their role in
enabling output elsewhere" (p. 34). The computed measure is better read as how
strongly a state draws from well-connected suppliers. The CCS 2026 abstract has
the same reading ("Its commodity flows sustain production in wealthier
states"), and its "Seven other physical-economy states show similar gains"
holds for five of the seven under the out-flow version.

**Not affected.** The GDP-eigenvector correlation, the 39% divergence count, the
boundary-sensitivity and filtration results, and the pre-registered stability
tests all use the in-flow values as reported. Betweenness and out-degree are
unaffected.

**Source.** `analysis/eigenvector_direction/check_direction.py` →
`output/direction.json`. Prompted by a question at the thesis defense (April 2026)
about left and right eigenvectors; confirmed and quantified in October 2026.

## 2. The set of structurally undervalued states (October 2026)

**What the thesis says.** Section 4 lists the "top overperformers" by eigenvector
divergence as KY (+14), MS (+10), MT (+8), LA (+7), SC (+7), TN (+6), MI (+6) and
IN (+6), and Section 5.4 refers to "the eight states this framework identifies as
structurally undervalued." Neither section states the rule that selects them.

**The issue.** No single threshold yields that list. North Dakota has the same
gap as Tennessee, Michigan and Indiana (GDP rank 46, eigenvector rank 40, +6) and
is not listed. A threshold of +6 selects nine states (the eight plus ND); the
threshold of 5 places used for the 39% divergence count selects eleven (adding
ND, WV and OK at +6, +5 and +5).

**Corrected statement.** A state is structurally undervalued when its
eigenvector (in-flow) rank is at least 5 places above its GDP rank, the same
threshold as the 39% count. In 2017 that is 11 states: KY, MS, MT, SC, LA, TN,
ND, MI, IN, WV and OK.

**Effect on results.** The divergence count, the correlation with GDP and the
ranks are unchanged. The data-center observation in Section 5.4 ("seven of the
eight") applies to the eight states as listed; it has not been checked for ND,
WV or OK and should not be extended to them without that check. Montana and
Louisiana also depend on the eigenvector direction (Section 1).
