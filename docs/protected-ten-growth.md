# Protecting the original ten under growth

The original ten Contract clauses are base coordinates, not a terminal list. Higher-order interactions may create new structure without receiving authority to erase, identify, or silently redefine the generators from which they arose.

Let

\[
A_0=\{a_1,\ldots,a_{10}\}.
\]

A protected realization in an ambient space \(X\) consists of an embedding \(\iota\) and recovery map \(r\) satisfying

\[
r\circ\iota=\operatorname{id}_{A_0}.
\]

This immediately implies that \(\iota\) is injective. The ten therefore remain distinguishable even when the ambient representation contains additional interaction structure.

For a growth step \(F:X\to Y\), with protected embeddings \(\iota_X\) and \(\iota_Y\), require the commuting condition

\[
F\circ\iota_X=\iota_Y.
\]

Then every original coordinate is still exactly recoverable after the step:

\[
r_Y(F(\iota_X(a_i)))=a_i.
\]

Consequently distinct protected coordinates cannot collapse under admissible growth.

The same criterion applies to a later quotient, projection, or representation map \(q:X\to Y\). If there exists a recovery map \(r_Y\) such that

\[
r_Y(q(\iota(a_i)))=a_i
\]

for every original coordinate, then \(q\circ\iota\) is injective. In linear language this corresponds to requiring that the kernel of the quotient avoid the protected singleton layer.

The interaction envelope remains separate. Ten generators have

\[
\binom{10}{2}=45
\]

possible pair supports,

\[
\binom{10}{3}=120
\]

possible triple supports, and

\[
\sum_{k=1}^{10}\binom{10}{k}=2^{10}-1=1023
\]

nonempty subset supports before feasibility, equivalence, symmetry, or validation removes or identifies them. These numbers are combinatorial upper envelopes, not claims of 1023 independent meanings.

A useful abstract grading is

\[
V=V^{(1)}\oplus V^{(\ge2)},
\qquad
V^{(1)}=\bigoplus_{i=1}^{10}V_{\{i\}},
\]

where the original ten occupy the protected singleton layer and higher-order residuals occupy separate interaction grades. A Möbius residual

\[
\Delta_S f=\sum_{T\subseteq S}(-1)^{|S|-|T|}f(1_T)
\]

can diagnose whether a higher-order support carries structure not reducible to lower-order terms. The present Lean module does not formalize that combinatorial or semantic novelty claim; it formalizes only preservation of the protected generators.

The operative invariant is therefore:

\[
\boxed{\text{growth may add structure, but every original coordinate remains recoverable.}}
\]

In a staged trajectory this becomes

\[
r_n\circ\iota_n=\operatorname{id}_{A_0}
\]

at every admitted stage, with commuting growth maps between stages. Discovery and admission may enlarge the held surface. Erasure or identification of a protected generator is a different operation and requires different authority.
