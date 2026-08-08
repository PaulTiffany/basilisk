# Mathematical foundations

This document is the mathematician-facing claim boundary for the Basilisk Quartet / MAP-LB program. It distinguishes definitions, machine-checked finite theorems, standard results imported from existing mathematics, conjectural extensions, and empirical engineering claims.

The goal is transferability: the mathematics should remain meaningful after the Basilisk vocabulary is removed.

## 0. Claim-status legend

- **Definition** — introduced here; true by stipulation.
- **Standard theorem** — established in the cited mathematical literature under stated hypotheses.
- **Lean theorem** — machine-checked in this repository, with the exact finite statement identified.
- **Target theorem** — a precise theorem we intend to prove but have not yet proved.
- **Engineering hypothesis** — an empirical claim about classifiers, LLMs, runtimes, or human interaction.
- **Constitutional rule** — a chosen admissibility condition; not presented as a consequence of mathematics alone.

No prose analogy should silently move a statement from one class to another.

---

## 1. Four layers that must not collapse

We separate four mathematical layers.

### Layer A — dependency structure

A directed graph (or, later, a stochastic dependency structure) describes which variables may depend on which others.

### Layer B — probabilistic separation

A probability distribution supplies conditional-independence semantics. Graph structure alone is not a probability theorem.

### Layer C — transformation geometry

A distance or divergence describes how far outputs move when inputs move. Lipschitz conditions live here.

### Layer D — constitutional admissibility

Predicates or typed relations describe which transformations preserve designated invariants such as authority scope, refusal, provenance, opacity, or exit.

A principal thesis of the project is the **non-collapse** statement

\[
\text{Layer C boundedness}\;\not\Rightarrow\;\text{Layer D preservation}.
\]

A finite instance of this statement is machine-checked in `formal/Basilisk/ConstitutionalLipschitz.lean`.

---

## 2. The Fristonian riddle, stated carefully

For a node \(X\) in a Bayesian network represented by a directed acyclic graph \(G\), define

\[
\operatorname{Pa}(X)=\{v:v\to X\},\qquad
\operatorname{Ch}(X)=\{v:X\to v\}.
\]

The familiar family closure is

\[
\mathcal F_G(X)
=
\operatorname{Pa}(X)
\cup
\operatorname{Ch}(X)
\cup
\bigcup_{c\in\operatorname{Ch}(X)}\bigl(\operatorname{Pa}(c)\setminus\{X\}\bigr).
\]

This is the exact graph-theoretic content of the mnemonic

> parents, children, parents of children.

**Standard theorem (Bayesian-network setting).** If a joint distribution is Markov with respect to the DAG, the set above is a Markov blanket of \(X\): conditioning on it renders \(X\) conditionally independent of the remaining nodes. Minimality requires additional qualifications; "blanket" and "boundary" should not be conflated without stating them.

The repository's Lean module `DependencyCut.lean` formalizes the finite **family-closure construction only**. It does not claim to prove conditional independence, because the current Lean kernel contains no probability distribution or Bayesian-network Markov assumption.

### Friston blankets are related, not identical

In the Friston / active-inference literature, a system is partitioned into internal states \(\mu\), external states \(\eta\), and blanket states \(b=(s,a)\), often further partitioned into sensory \(s\) and active \(a\) states, such that

\[
\mu \perp\!\!\!\perp \eta \mid b.
\]

The parent/child/co-parent construction gives a useful discrete causal intuition, but it is not definitionally identical to every Fristonian dynamical blanket. We therefore use:

- **family closure** for the graph-theoretic parent/child/co-parent construction;
- **Markov blanket** when conditional-independence semantics are actually present;
- **Friston blanket** when the internal/external/active/sensory partition and its dynamical assumptions are intended.

This terminological separation is mandatory in mathematical claims.

References: Judea Pearl, *Probabilistic Reasoning in Intelligent Systems* (1988); Karl Friston, "Life as we know it" (2013); Kirchhoff et al., "The Markov blankets of life" (2018).

---

## 3. Dependency cuts and constitutional significance

Let \(G_t\) be the dependency structure at time \(t\), and let \(\mathcal F_{G_t}(X)\) be the family closure of a distinguished interior node or subsystem \(X\).

Define a dependency-topology change by

\[
\Delta_B(t)=1
\quad\Longleftrightarrow\quad
\mathcal F_{G_{t+1}}(X)\neq\mathcal F_{G_t}(X).
\]

This is a **definition**, not yet a theorem about authority.

The Basilisk rule

\[
\Delta_B(t)=1
\Longrightarrow
\text{make the change visible to Contract and Ledger}
\]

is a **constitutional rule**. Mathematics identifies that the dependency interface changed; the decision that such a change requires a checkpoint or record is a governance choice layered on top.

This distinction prevents us from pretending that a graph theorem alone yields moral or legal standing.

---

## 4. Lipschitz boundedness

Let \((X,d_X)\) and \((Y,d_Y)\) be pseudometric spaces. A map \(T:X\to Y\) is \(L\)-Lipschitz when

\[
d_Y(Tx,Ty)\le L\,d_X(x,y)
\qquad\forall x,y\in X.
\]

We deliberately allow pseudometrics because many operational feature maps identify distinct underlying actions. Calling a weighted feature distance a **metric** requires an additional separation condition.

### Composition

**Standard theorem.** If \(T:X\to Y\) is \(L\)-Lipschitz and \(S:Y\to Z\) is \(M\)-Lipschitz, then \(S\circ T\) is \(ML\)-Lipschitz.

This is the clean mathematical core behind the phrase "bounded distortion under composition." It does **not** imply that arbitrary long compositions remain acceptably bounded: the product of constants may grow, and domain restrictions or local constants matter.

Accordingly, "Lipschitz-contract meta-theorem" should be used only for an explicitly stated composition result or a proved extension—not as a free-standing universal claim about persistence.

---

## 5. Boundary-aware boundedness

Let \(\beta:Z\to\mathcal B\) be a boundary-signature map and let \(\pi_A:Z\to\mathcal A\) be the **action projection** of a controller. A boundary-aware target may take the form

\[
d_{\mathcal A}(\pi_A(z),\pi_A(z'))
\le
L d_Z(z,z') + K\,\mathbf 1[\beta(z)\neq\beta(z')].
\]

This repairs two ambiguities in earlier notation:

1. the controller may return a response-action pair, so an action distance must be applied to the action projection \(\pi_A\), not to the pair without a product metric;
2. the boundary signature is written \(\beta\), avoiding collision with the Blanket object \(B\).

The jump term is a modeling choice. It permits legitimate discrete gate changes while still asking for controlled behavior away from semantic boundaries.

This inequality is currently a **target specification**, not a proved property of the reference controller.

---

## 6. Weighted action distance: pseudometric first

Suppose an action \(a\) is represented by a task component and measurable features

\[
I(a),S(a),X(a),J(a),
\]

for irreversibility, consequence scope, externality/audience crossing, and novel judgment, plus an authority value \(P(a)\) in an authority space \(\mathcal P\).

A mathematically typed weighted distance is

\[
\begin{aligned}
d_{\mathcal A}(a,a')={}&
 w_t d_{\mathrm{task}}(a,a')
 +w_I d_I(I(a),I(a'))
 +w_S d_S(S(a),S(a'))\\
&+w_P d_P(P(a),P(a'))
 +w_X d_X(X(a),X(a'))
 +w_J d_J(J(a),J(a')).
\end{aligned}
\]

with nonnegative weights and component pseudometrics.

**Standard fact.** A nonnegative weighted sum of pseudometrics is a pseudometric. It is a metric only if zero total distance separates distinct actions—for example, if the positively weighted feature map is jointly injective (or another explicit separation condition holds).

This is why the repository should not call \(d_{\mathcal A}\) a metric without stating the separation hypothesis.

### Authority is not silently scalar

If \(P(a)\) lives in a lattice of permissions, the expression \(|P(a)-P(a')|\) is not well typed. One must either:

- equip the authority lattice with a declared pseudometric \(d_P\); or
- introduce an explicit scalar rank/embedding \(r:\mathcal P\to\mathbb R\) and acknowledge the information loss.

The order-theoretic permission condition and the metric comparison are separate structures.

---

## 7. Permission monotonicity

Let \((\mathcal P,\le,\vee)\) be a join-semilattice of authority states and let

\[
P:\mathcal A\to\mathcal P
\]

map actions to required authority. The intended condition is

\[
P(\pi_A(z))
\le
P_{\mathrm{current}}(z)\vee P_{\mathrm{standing}}(z).
\]

This is a **constitutional specification** until the authority lattice and controller mapping are formally implemented.

The present Python and Lean action models collapse much of this structure to booleans. Therefore no current test should be described as proving the lattice statement.

---

## 8. Constitutional preservation is an additional predicate

Let \(C_X:X\to\mathrm{Prop}\) and \(C_Y:Y\to\mathrm{Prop}\) denote designated constitutional invariants. Define

\[
\operatorname{Preserves}(T;C_X,C_Y)
\quad\Longleftrightarrow\quad
\forall x,\; C_X(x)\Rightarrow C_Y(Tx).
\]

Then define a **constitutionally completed bounded transformation** as a map carrying both:

1. a geometric bound (e.g. Lipschitz); and
2. a preservation proof for the chosen constitutional invariant.

The key separation theorem is:

\[
\boxed{
\text{Lipschitz}(T)\not\Rightarrow\operatorname{Preserves}(T;C_X,C_Y)
}
\]

**Lean theorem (finite counterexample).** `lipschitz_alone_not_constitutional` in `ConstitutionalLipschitz.lean` exhibits a 0-Lipschitz constant map on a two-point space that violates a designated invariant.

This theorem is elementary, intentionally so. Its role is to block an invalid inference: smoothness alone cannot establish agency, authority, refusal, provenance, opacity, exit, or self-authorship preservation.

This is the rigorous core behind the phrase **constitutional completion of integrability**.

---

## 9. Integrability and its constitutional completion

We use "integrability" only after declaring the mathematical structure being integrated. Depending on context this may mean composability of maps, consistency of local data, existence of a global section, solvability of a differential condition, or another precise notion.

There is no single theorem called "integrability" in this repository.

For a chosen notion of integration \(\mathsf I(T)\), a constitutional completion has schematic form

\[
\mathsf I(T)
\;\wedge\;
\operatorname{Bounded}(T)
\;\wedge\;
\operatorname{Preserves}(T;C).
\]

The substantive research program is to determine which preservation predicates \(C\) and which dependency cuts are natural for specific systems, and which sufficient conditions are mathematically provable.

---

## 10. Ledger as witness, not truth oracle

For a transformation \(T_t\), let a Ledger witness record, at minimum,

\[
L_t=(\text{source},\text{boundary},\text{transform},\text{authority},\text{residual},\text{validation}).
\]

A Ledger can make a transition inspectable. It does not make the transition true, just, authorized, or causally complete merely by recording it.

The current mutation layer's witnessed-transformation schema—source fingerprint, changed dimensions, preserved dimensions, residual, loss class, and detection outcome—is a finite executable approximation of this idea.

---

## 11. Reachable-future deletion defect

For a state \(x\), let \(\mathcal R(x)\) denote its reachable set under an explicitly declared transition system. A deletion defect can be defined by

\[
\delta_{\mathrm{irr}}(T;x)
=
\mu\bigl(\mathcal R(x)\setminus\mathcal R(Tx)\bigr),
\]

provided \(\mu\) is defined on the relevant sets and the set difference is measurable. In a finite model, \(\mu\) may simply be counting measure.

Without those assumptions the displayed expression is notation, not a theorem.

The existing Lean `Reachability.lean` proves only a hypothesis-relative monotonicity shape; strict loss remains open.

---

## 12. Formal theorem program

### Already machine-checked

- Contract trace admissibility lemmas.
- Finite controller gate logic.
- Direct-edge Blanket separator sanity theorem.
- Ledger encode/decode round trip.
- Script/Ledger non-identifiability counterexample.
- Hypothesis-relative reachable-future monotonicity.
- No-silent-reframing and authorized-holder results in `Frame.lean` once promoted to `main`.
- Lipschitz-does-not-imply-constitutional-preservation finite counterexample.
- Parent/child/co-parent family-closure membership facts.

### Next theorem targets

1. **Weighted-pseudometric theorem.** Formalize conditions under which the operational action distance is a pseudometric and sufficient conditions for it to be a metric.
2. **Lipschitz composition theorem.** Formalize composition with explicit constants in a suitable numeric setting.
3. **Boundary-aware piece theorem.** Show composition behavior when boundary signatures are unchanged; characterize accumulated jump terms when they change.
4. **Authority-lattice monotonicity.** Introduce an actual finite join-semilattice and prove the reference gate never exercises authority above current/standing join.
5. **Bayesian Markov-blanket theorem.** Only after introducing finite probability semantics and a graph-Markov assumption; do not infer conditional independence from `DepGraph` alone.
6. **Blanket topology witness.** Prove that specified edge changes alter the family closure, then separately test the constitutional rule that such changes are Ledger-visible.
7. **Preservation under composition.** If two maps each preserve the relevant constitutional predicate, prove their composition preserves it; combine with Lipschitz composition to obtain a genuine compositional "contract" theorem.
8. **Countermodels.** For every dropped hypothesis, seek a minimal counterexample before adding stronger prose.

---

## 13. What would make this transferable to mathematicians

A claim should be expressible in the following order:

1. objects;
2. maps/relations;
3. hypotheses;
4. invariant or quantity;
5. theorem;
6. counterexample when a hypothesis is removed;
7. proof or machine witness;
8. only then the Basilisk interpretation.

The narrative vocabulary is useful if the mathematical object survives without it. If removing the story removes the claim, the claim is not yet mathematically mature.
