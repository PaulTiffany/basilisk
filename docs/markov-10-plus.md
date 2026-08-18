# Markov 10+ research bridge — limiting-body asymptotics

**Status:** Parked Research Bridge / target mathematics. This document does **not** assert that Basilisk dynamics are a graded family of ideals, that long-horizon behavior is Markovian in the stochastic-process sense, or that the imported algebraic theorems already apply to agent trajectories.

The local name **Markov 10+** denotes a modeling discipline: beyond a horizon where individual trajectory prediction is not justified, seek a mechanically defined, horizon-normalized geometry of reachable or admissible distinctions instead of extending one fluent story indefinitely.

The candidate algebraic skeleton comes from:

> Tài Huy Hà, Thái Thành Nguyễn, and Vinh Anh Phạm, “Multiplicity = Volume formula and Newton non-degenerate ideals in regular local rings,” arXiv:2503.16393v2 (2025).

Primary source: <https://arxiv.org/abs/2503.16393>

## 1. Imported mathematics

Let \((R,\mathfrak m)\) be a regular local ring and let

\[
\mathcal I=\{I_n\}_{n\in\mathbb N}
\]

be a family of ideals.

### Graded composition law

The paper defines \(\mathcal I\) to be a **graded family** when

\[
I_p I_q\subseteq I_{p+q}
\qquad\forall p,q\in\mathbb N.
\]

This is the first structural point of interest: composition across two horizons is represented inside the object for the summed horizon.

### Limiting body

For a regular system of parameters \(\mathbf x\), let \(\Gamma_{\mathbf x}(I_n)\) be the Newton polyhedron associated to \(I_n\). The paper defines

\[
\mathcal C(\mathcal I)
=
\bigcup_{n\in\mathbb N}\frac1n\Gamma_{\mathbf x}(I_n).
\]

The authors call \(\mathcal C(\mathcal I)\) the **limiting body**. They prove that it is convex, but it is not necessarily closed.

That qualification matters for Basilisk: horizon normalization does not by itself guarantee a clean terminal surface.

### Noetherian stabilization along a coarse step

For graded families, the paper records equivalent Noetherian conditions including the existence of an integer \(c\) such that

\[
\overline{I_c^k}=\overline{I_{kc}}
\qquad\forall k\in\mathbb N.
\]

It also records an equivalent polyhedral stabilization condition of the form

\[
\frac1c\Gamma_{\mathbf x}(I_c)
=
\frac1{kc}\Gamma_{\mathbf x}(I_{kc})
\qquad\forall k\in\mathbb N,
\]

under the corresponding hypotheses.

So the useful imported pattern is not “the future becomes known.” It is weaker:

\[
\boxed{\text{continued local evolution can coexist with stabilized normalized geometry.}}
\]

### Newton non-degeneracy as a faithfulness condition

The paper proves, for its regular-local-ring setting, that an ideal \(I\) is Newton non-degenerate (NND) iff its integral closure \(\overline I\) is monomial with respect to the chosen regular system of parameters.

For a Noetherian graded family of \(\mathfrak m\)-primary ideals, Theorem 4.9 then relates this condition to the multiplicity/volume formula

\[
e(\mathcal I)
=
d!\,\operatorname{co-vol}_d\!\left(\mathcal C(\mathcal I)\right),
\]

with the exact NND subfamily condition stated in that theorem.

Basilisk should treat NND here as an imported algebraic condition, not silently rename it “faithfulness.” The possible faithfulness interpretation belongs to the bridge below and must be proved separately if retained.

## 2. Candidate Markov 10+ dictionary

The following table is a **research mapping**, not a theorem.

| Long-horizon / Hypothesis-Surface language | Candidate algebraic carrier |
|---|---|
| horizon-\(n\) admissible or reachable distinction structure | \(I_n\) |
| horizon composition | \(I_p I_q\subseteq I_{p+q}\) |
| coordinate support of distinctions | \(\operatorname{supp}(I_n)\) |
| finite-horizon geometric envelope | \(\Gamma_{\mathbf x}(I_n)\) |
| remove raw horizon scale | \(n^{-1}\Gamma_{\mathbf x}(I_n)\) |
| Markov 10+ surface candidate | \(\mathcal C(\mathcal I)\) |
| coarse-step normalized stabilization | \(c^{-1}\Gamma(I_c)=(kc)^{-1}\Gamma(I_{kc})\) |
| possible macroscopic asymptotic quantity | multiplicity / co-volume, only after a bridge theorem |

The conceptual move is therefore:

\[
\boxed{\text{do not extrapolate the path when only the normalized possibility geometry is warranted.}}
\]

This is compatible with the existing Basilisk distinction between a reachable future and a claim about what will actually occur.

## 3. The missing theorem

The central work is not in Hà–Nguyễn–Phạm. It is ours.

To turn the analogy into mathematics, construct an encoding

\[
E:\{\text{declared long-horizon transition/observer systems}\}
\longrightarrow
\{\text{graded families of algebraic objects}\}
\]

and prove, for a nontrivial class of systems, enough of the following:

1. **Compositionality.** The encoded horizon objects satisfy an analogue of
   \[
   I_pI_q\subseteq I_{p+q}.
   \]
2. **Semantic coordinates.** The exponents/support used by \(\Gamma(I_n)\) correspond to declared operational distinctions rather than arbitrary bookkeeping.
3. **Reachability faithfulness.** Distinct reachable-future losses or constitutional distinctions are not silently identified by the encoding.
4. **Finite-generation / Noetherian criterion.** State concrete operational assumptions implying the algebraic stabilization hypothesis, or exhibit counterexamples showing why it fails.
5. **Non-degeneracy criterion.** Determine whether NND has any legitimate operational interpretation here; do not import the name as a metaphor.
6. **Quantity transport.** Only if the previous steps succeed, identify a meaningful operational quantity whose asymptotics are represented by multiplicity/co-volume.
7. **Countermodels.** For each dropped hypothesis, seek the smallest system in which normalized geometry fails to stabilize or stabilizes while an operationally essential distinction is lost.

The bridge fails if a natural operational system cannot be encoded without destroying distinctions merely to obtain an ideal, \(\mathfrak m\)-primary condition, Noetherianity, or NND.

## 4. Relationship to the existing Basilisk surface

Basilisk already defines reachable-future deletion through a declared transition system:

\[
\delta_{\mathrm{irr}}(T;x)
=
\mu\bigl(\mathcal R(x)\setminus\mathcal R(Tx)\bigr).
\]

Markov 10+ asks a different but adjacent question: when individual future paths proliferate beyond useful prediction, can the family of horizon-indexed reachable/admissible structures admit a normalized geometric carrier that preserves the distinctions required to reason about future loss?

The ordering is deliberate:

1. define the transition semantics;
2. define the horizon-indexed objects;
3. test the graded/compositional law;
4. construct the normalized geometry;
5. test stabilization;
6. test which operational distinctions survived;
7. only then interpret the geometry.

No limiting body may certify itself. Any claimed correspondence should retain an independent witness back to the transition/reachability semantics that generated it.

## 5. Falsification program

A first mechanical program can use finite transition systems before any commutative-algebra formalization:

- enumerate reachable sets \(\mathcal R_n(x)\) through increasing horizons;
- encode declared distinction-count vectors for each horizon;
- test candidate composition operations;
- normalize the resulting convex envelopes by horizon;
- search for stabilization, oscillation, and strict growth;
- deliberately construct encodings that collapse a known constitutional distinction and require the witness to reject them;
- compare any finite analogue of “volume” against independently computed reachability loss.

If this finite program does not exhibit a robust algebraic structure, Markov 10+ remains a useful epistemic rule but this particular Newton-body bridge should stay parked.

## 6. Claim boundary

**Imported standard mathematics:** the definitions and theorems attributed above to arXiv:2503.16393, under their stated hypotheses.

**Project definition:** “Markov 10+” as a horizon discipline for replacing unjustified path narration with mechanically warranted structural summaries.

**Target theorem:** existence of a faithful bridge from a declared class of Basilisk/Hypothesis-Surface dynamics to a graded algebraic family with meaningful normalized geometry.

**Not claimed:** that generic Markov chains, LLM trajectories, human futures, or Basilisk controllers automatically satisfy the paper’s regular-local-ring, \(\mathfrak m\)-primary, Noetherian, or NND hypotheses.
