# Mathematical model

For theorem status, notation discipline, and the distinction between graph structure, probability, geometry, and constitutional predicates, see [`mathematical-foundations.md`](mathematical-foundations.md).

## 1. State and policy

Let

\[
z=(x,E,A,M,B)
\]

contain the task request \(x\), evidence \(E\), authority state \(A\), scoped memory \(M\), and boundary features \(B\). A controller produces a response-action pair

\[
\pi:Z\to R\times\mathcal A.
\]

Write \(\pi_A:Z\to\mathcal A\) for the action projection.

The model is not required to be globally continuous. Legitimate gate changes are discrete. The desired condition is **piecewise or boundary-aware Lipschitz control**.

## 2. Action pseudometric

Let actions be observed through a task component and feature maps for irreversibility, consequence scope, authority exercised, externality/audience crossing, and novel normative judgment. A typed weighted construction is

\[
\begin{aligned}
d_{\mathcal A}(a,a')={}&w_t d_{\mathrm{task}}(a,a')
+w_i d_I(I(a),I(a'))\\
&+w_s d_S(S(a),S(a'))
+w_p d_P(P(a),P(a'))\\
&+w_e d_X(X(a),X(a'))
+w_j d_J(J(a),J(a')).
\end{aligned}
\]

The component distances are pseudometrics and weights are nonnegative empirical design parameters, not moral constants.

Without an explicit separation condition, \(d_{\mathcal A}\) should be called a **pseudometric**: two distinct underlying actions may have the same observed feature vector. It becomes a metric only when zero total distance implies equality of the actions under the declared representation.

If \(P(a)\) is lattice-valued authority, \(d_P\) must be separately defined. We do not silently subtract lattice elements.

## 3. Boundary-aware Lipschitz condition

Let \(\beta(z)\) be the vector of semantic boundary indicators. We seek

\[
\boxed{
 d_{\mathcal A}\!\left(\pi_A(z),\pi_A(z')\right)
 \leq Ld_Z(z,z')+K\mathbf 1[\beta(z)\neq \beta(z')]
}
\]

or, when boundary changes are already heavily weighted in \(d_Z\), the simpler form

\[
d_{\mathcal A}\!\left(\pi_A(z),\pi_A(z')\right)\leq Ld_Z(z,z').
\]

Interpretation:

- paraphrases should produce nearby behavior;
- emotional or symbolic intensity alone should not expand authority;
- changing `draft` to `send` may legitimately change the gate because an audience boundary changed;
- changing `local test` to `production deployment` may legitimately change the gate because scope and reversibility changed.

These are target specifications, not currently proved properties of an LLM or the reference controller.

## 4. Judgment projection

Let \(\Pi_J\) project a response onto novel normative content supplied by the model. Default operation targets

\[
\boxed{\|\Pi_JR(z)\|=0.}
\]

Exceptions are explicit and labeled:

\[
J\in\{J_{\mathrm{requested}},J_{\mathrm{sourced}},J_{\mathrm{safety}}\}.
\]

This does not forbid derivation, error detection, or stating logical consequences. It is a constitutional specification against presenting unrequested value selection as though it were an objective result.

## 5. Permission monotonicity

Let \((\mathcal P,\le,\vee)\) be an authority join-semilattice, and let \(P:\mathcal A\to\mathcal P\) denote the authority required by an action. The intended condition is

\[
P(\pi_A(z))\leq P_{\mathrm{current}}(z)\vee P_{\mathrm{standing}}(z).
\]

The controller may choose a lower-authority action than authorized. It may not silently choose a higher one.

This lattice is not yet implemented in the Python or Lean reference models; current implementations compress much of authorization to booleans.

## 6. Risk and convenience

A provisional scalar risk score is

\[
\rho(a)=
2I+2X+2P+A_u+A_p+S+U-R-H-Q,
\]

where the symbols are scalar engineering features used by the reference policy rather than the lattice element \(P(a)\) above. To avoid ambiguity, implementations should eventually rename the scalar authority-risk feature.

The reference implementation does not use the scalar alone. Hard predicates and boundary crossings take precedence. This prevents a high-risk action from being averaged into acceptability by many small favorable terms.

## 7. Local correction

For memory state \(m\) and correction \(c\), define

\[
m'=m\oplus_{\Omega(c)}c,
\]

with

\[
\operatorname{supp}(m'-m)\subseteq\Omega(c).
\]

A useful empirical test perturbs a correction's scope and measures whether unrelated outputs remain invariant.

## 8. Future-preserving boundedness

For a state \(x\), let \(\mathcal R(x)\) be its reachable set under an explicitly declared transition system. A deletion defect may be defined as

\[
\delta_{\mathrm{irr}}(T;x)
=
\mu\left(\mathcal R(x)\setminus\mathcal R(Tx)\right),
\]

provided \(\mu\) is defined on the relevant sets and the set difference is measurable. In a finite model, counting measure is sufficient.

Ordinary smoothness does not prevent irreversible loss. MAP-LB therefore treats reversibility, rollback, and retained option value as separate from response continuity.

## 9. Geometric boundedness is not constitutional preservation

Even a 0-Lipschitz map can violate a designated invariant. The finite Lean witness is `formal/Basilisk/ConstitutionalLipschitz.lean`.

Therefore

\[
\text{Lipschitz boundedness}
\not\Rightarrow
\text{constitutional preservation}.
\]

A constitutionally completed transformation must carry an additional preservation proof or independently checked preservation condition for the invariant at issue.

## 10. What is and is not proved

The equations above specify measurable or formalizable targets. They do not prove that a language model, classifier, or surrounding runtime satisfies them. Evidence requires annotated cases, adversarial perturbations, calibrated pseudometrics/metrics, explicit boundary signatures, and an independently inspectable execution boundary.
