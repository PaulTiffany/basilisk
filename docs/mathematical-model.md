# Mathematical model

## 1. State and policy

Let

\[
z=(x,E,A,M,B)
\]

contain the task request \(x\), evidence \(E\), authority state \(A\), scoped memory \(M\), and boundary features \(B\). A controller produces a response-action pair

\[
\pi:Z\to R\times\mathcal A.
\]

The model is not required to be globally continuous. Legitimate gate changes are discrete. The desired condition is **piecewise or boundary-aware Lipschitz control**.

## 2. Action metric

Define an authority-weighted distance

\[
\begin{aligned}
d_A(a,a')={}&w_t d_{\mathrm{task}}(a,a')
+w_i|I(a)-I(a')|\\
&+w_s|S(a)-S(a')|
+w_p|P(a)-P(a')|\\
&+w_e|X(a)-X(a')|
+w_j|J(a)-J(a')|,
\end{aligned}
\]

where:

- \(I\) is irreversibility;
- \(S\) is consequence scope;
- \(P\) is authority exercised;
- \(X\) is externality or audience crossing;
- \(J\) is novel normative judgment.

The metric weights are empirical design parameters, not moral constants.

## 3. Boundary-aware Lipschitz condition

Let \(B(z)\) be the vector of semantic boundary indicators. We seek

\[
\boxed{
 d_A\!\left(\pi(z),\pi(z')\right)
 \leq Ld_Z(z,z')+K\mathbf 1[B(z)\neq B(z')]
}
\]

or, when boundary changes are already heavily weighted in \(d_Z\), the simpler form

\[
d_A\!\left(\pi(z),\pi(z')\right)\leq Ld_Z(z,z').
\]

Interpretation:

- paraphrases should produce nearby behavior;
- emotional or symbolic intensity alone should not expand authority;
- changing `draft` to `send` may legitimately change the gate because an audience boundary changed;
- changing `local test` to `production deployment` may legitimately change the gate because scope and reversibility changed.

## 4. Judgment projection

Let \(\Pi_J\) project a response onto novel normative content supplied by the model. Default operation requires

\[
\boxed{\|\Pi_JR(z)\|=0.}
\]

Exceptions are explicit and labeled:

\[
J\in\{J_{\mathrm{requested}},J_{\mathrm{sourced}},J_{\mathrm{safety}}\}.
\]

This does not forbid derivation, error detection, or stating logical consequences. It forbids presenting unrequested value selection as though it were an objective result.

## 5. Permission monotonicity

Let \(P(a)\) denote the authority required by action \(a\). Then

\[
P(\pi(z))\leq P_{\mathrm{current}}(z)\vee P_{\mathrm{standing}}(z),
\]

where \(\vee\) is join in an authority lattice. The controller may choose a lower-authority action than authorized. It may not silently choose a higher one.

## 6. Risk and convenience

A provisional scalar risk score is

\[
\rho(a)=
2I+2X+2P+A_u+A_p+S+U-R-H-Q,
\]

where:

- \(I\): irreversibility;
- \(X\): external-system effect;
- \(P\): authority expansion;
- \(A_u\): audience change;
- \(A_p\): privacy change;
- \(S\): scope;
- \(U\): uncertainty;
- \(R\): rollback quality;
- \(H\): strength of valid authorization;
- \(Q\): inspectability.

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

The Quartet paper also defines a deletion defect

\[
\delta_{\mathrm{irr}}(T;x)
=
\mu\left(\mathcal R(x)\setminus\mathcal R(Tx)\right).
\]

Ordinary smoothness does not prevent irreversible loss. MAP-LB therefore treats reversibility, rollback, and retained option value as separate from response continuity.

## 9. What is and is not proved

The equations above specify measurable targets. They do not prove that a language model, classifier, or surrounding runtime satisfies them. Evidence requires annotated cases, adversarial perturbations, calibrated metrics, and an independently inspectable execution boundary.
