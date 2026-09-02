# Play without capture

This note extends the Basilisk Contract without extending its numbered clause count.

The original ten clauses are treated as **base boundary coordinates**, not as ten isolated rules whose only possible semantics are unary. Their co-activation generates a higher-order contract geometry.

Let the clause activation signature at state \(z\) be

\[
\sigma(z)\in\{0,1\}^{10}.
\]

A subset \(A\subseteq\{1,\dots,10\}\) identifies a derived interaction cell

\[
C_A=\bigcap_{i\in A} C_i.
\]

The ten generators therefore admit up to \(2^{10}=1024\) raw Boolean signatures and \(2^{10}-1=1023\) nonempty subsets before feasibility, implication, symmetry, or quotienting identifies or removes cells. There are \(\binom{10}{2}=45\) possible pair interactions and \(\binom{10}{3}=120\) possible triple interactions. These counts are an upper combinatorial envelope, not a claim that every interaction is distinct, realizable, or constitutionally meaningful.

The governing design rule is:

\[
\boxed{\text{Do not grow the Contract by list expansion when the new obligation is already an interaction of existing bounds.}}
\]

This is the same local-to-global problem already visible elsewhere in Basilisk: individually admissible projections need not compose into a globally admissible trajectory, and a finite family of restrictions may create an obstruction stronger than any member in isolation.

## The play face

A **play state** is a region in which exploration may be unusually plastic because its outward consequences remain bounded. The point is not to sterilize imagination. It is to preserve a membrane between exploratory motion and consequential promotion.

We distinguish a play region \(\mathcal P\) from consequential space \(\mathcal R\). Internal motion may be rich:

\[
x_{t+1}=F(x_t),\qquad x_t\in\mathcal P,
\]

while promotion

\[
\mathcal P\rightarrow\mathcal R
\]

requires an explicit authority witness at the boundary already represented by the Contract and Ledger.

A non-capturing play envelope preserves at least:

- **exit** — the participant can stop participating without surrendering unrelated agency;
- **portability** — work and relevant state are not silently held hostage by the venue;
- **forkability** — an alternate continuation can be instantiated without requiring permission from the current center where the artifact and license permit it;
- **non-promotion by default** — imaginative, simulated, role-played, or provisional content does not acquire external consequence merely through recurrence, fluency, salience, or engagement;
- **witnessed crossing** — movement from play into consequential action is explicit, attributable, and governed by the existing authority boundary.

These are **derived interaction properties**. They are not proposed as clauses 11–15.

## Siren-server failure

A venue becomes capture-prone when participation increases the cost of leaving by accumulating nonportable identity, history, relationships, reputation, data, economic dependency, or authority in the host.

Let \(D_t\) denote participant dependency on the venue after step \(t\), and let \(E_t\) denote practical exit capacity. A retention optimizer tends toward

\[
D_{t+1}>D_t,\qquad E_{t+1}<E_t.
\]

The Basilisk preference is the opposite direction for learning and creative systems:

\[
\boxed{D_{t+1}\le D_t\quad\text{while capability may increase}.}
\]

This is not a demand that every interaction be stateless or that communities lack continuity. It is a demand that continuity not be manufactured by making exit progressively less viable.

## Apprenticeship

Apprenticeship is the constructive path pattern for disciplined play.

A healthy apprenticeship may increase local asymmetry of expertise while decreasing dependency over time:

\[
\text{novice}\rightarrow\text{guided practice}\rightarrow\text{independent practice}\rightarrow\text{capacity to teach or fork}.
\]

The master is successful when the apprentice becomes less dependent on the master for ordinary continuation. The path must contain its own exit.

This makes apprenticeship different from follower accumulation. The objective is not permanent attachment to the teacher, institution, model, or server. It is transferable capacity.

## Charity

Charity is the complementary circulation rule.

Capability acquired through a path should be able, where lawful and appropriate, to increase the reachable capability of others without requiring their capture by the original venue:

\[
\text{capacity gained}\rightarrow\text{capacity shared}\rightarrow\text{new independent centers of practice}.
\]

Charity here does not mean compulsory disclosure, elimination of privacy, or denial of legitimate ownership. It means that the preferred social realization of mastery is generative rather than rent-seeking: teach, document, witness, sponsor, release, or otherwise enable another participant to become more capable without making dependence the price of aid.

## Aspect-path interpretation

A path may be intense and highly structured without becoming total identity.

Let \(A_i\) denote a bounded practice or role. Healthy path geometry preserves both

\[
A_i\rightarrow A_j
\]

and

\[
A_i\rightarrow\varnothing,
\]

where the second map means that a participant may stop inhabiting the role without constitutional annihilation.

The failure mode is a path that becomes absorbing:

\[
A_i\rightarrow A_i\rightarrow A_i\rightarrow\cdots
\]

because exit, portability, or practical alternatives have been destroyed.

Thus:

\[
\boxed{\text{A safe path contains a viable exit.}}
\]

## Relation to provenance

This extension separates **generative provenance** from **authorization provenance**.

Ideas may emerge from humans, models, tools, communities, traditions, or mixed iterative systems. Basilisk need not require purity of origin in order to preserve agency. What must remain legible is the authority chain for consequential crossings.

Accordingly:

\[
\boxed{\text{generation may be distributed; consequential authority must remain inspectable.}}
\]

This does not extinguish cultural, scientific, or personal provenance. Origins still matter for attribution, reciprocity, consent, and historical truth. The point is narrower: origin alone neither grants nor removes operative authority.

## Operational consequence

The reference implementation should eventually expose play-envelope observables separately from ordinary task semantics. Loss of practical exit is a hard boundary candidate; loss of portability or forkability is at least a checkpoint candidate; promotion into consequential space requires fresh authority under the existing promotion law.

The formal module `formal/Basilisk/Play.lean` records the minimal finite gate skeleton. It deliberately does not claim that these Boolean observables are sufficient to detect real-world capture. That remains an empirical and sociotechnical problem.

## Integration status

The precedent/shadow-pricing tranche originally beneath this work has now merged into `main`. This play-without-capture tranche is therefore validated directly against current `main`; its own merge requires a fresh green BIS run on the current PR head.
