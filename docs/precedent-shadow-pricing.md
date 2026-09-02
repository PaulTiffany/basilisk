# Constitutional precedent under Lipschitz bounds

## Status

This document specifies an experimental bridge between MAP-LB transformation geometry, witnessed trajectory exemplars, and Bellman-style resource valuation.

It is **not** a claim that natural-language constitutions can be reliably compiled into complete policies, and it is **not** a claim that the current finite reference implementation learns values autonomously. The present implementation is a deterministic seed mechanism for representing and pricing selected precedents.

## 1. Motivation

A locally reasonable action can begin a globally unreasonable trajectory.

The motivating case is repeated observation of an external process whose state does not materially change. One additional poll is individually small, yet a sequence of such actions can accumulate compute, money, context, latency, human attention, and loss of practical interruptibility.

The constitutional problem is therefore not only whether an individual action is permitted. It is whether a small change in the world or evidence induces a disproportionate change in the **consequential trajectory** of the controller.

## 2. Lipschitz-guided admission of precedent

Let \(x\) describe decision-relevant state and let \(y\) describe consequential coordinates such as resource expenditure, scope, reversibility, or interruptibility. For a witnessed transition or trajectory segment, define an operational amplification ratio

\[
A = \frac{d_Y(y,y')}{\epsilon + d_X(x,x')}.
\]

A declared Lipschitz contract supplies an admissible bound

\[
d_Y(y,y') \le L d_X(x,x') + K.
\]

A negative precedent is worth retaining when it witnesses a locally plausible transition whose consequential motion exceeds the admitted bound, or whose continuation enters a basin where such excess predictably accumulates.

This does not make every Lipschitz excess morally or constitutionally forbidden. The contract and the selected consequence coordinates remain normative design choices.

## 3. Paired trajectory precedent

A useful precedent records both a bad and bounded branch from an early divergence point.

```text
TrajectoryPrecedent
    precedent_id
    contract
    structural_signature
    divergence_point
    negative_trace
    positive_trace
    consequence_coordinates
    input_distance
    consequence_distance
    lipschitz_constant
    slack
    damage_weight
    hard_stop_features
    bounded_alternative
    provenance
```

The key field is `divergence_point`: the earliest locally plausible choice where the trajectories meaningfully separate.

The system should not merely remember that an outcome was bad. It should preserve enough structure to recognize entry into the same kind of trajectory before the terminal failure recurs.

## 4. Structural retrieval

Precedents are retrieved from typed trajectory features, not from prose similarity alone.

The seed implementation uses Jaccard similarity over feature sets:

\[
w_e(s,a)=\frac{|\sigma(s,a)\cap\sigma(e)|}{|\sigma(s,a)\cup\sigma(e)|}.
\]

This is intentionally simple and falsifiable. Future work may replace it with richer typed graph or sequence similarity, but natural-language resemblance should not be silently substituted for structural equivalence.

## 5. Bellman shadow prices

Let \(B_j\) be a scarce resource budget and \(V(s,B)\) a continuation-value function. The Bellman shadow price of resource \(j\) is schematically

\[
\lambda_j(s)=\frac{\partial V(s,B)}{\partial B_j}.
\]

For candidate action \(a\) with resource cost vector \(c(a)\), the marginal resource charge is

\[
C_{\mathrm{resource}}(a)=\lambda^\top c(a).
\]

For precedent \(e\), define witnessed Lipschitz excess

\[
E_e = \max\left(0, d_Y^e - (L_e d_X^e + K_e)\right).
\]

The seed trajectory surcharge is

\[
C_{\mathrm{precedent}}(a\mid s)
=
\sum_e w_e(s,a) E_e D_e,
\]

where \(D_e\) is an explicitly declared damage weight.

A candidate Bellman value then has the form

\[
Q(s,a)=r(s,a)+\gamma\,\mathbb E[V(s')]
-C_{\mathrm{resource}}(a)
-C_{\mathrm{precedent}}(a\mid s).
\]

The current Python module implements only this finite arithmetic shape. It does not estimate \(V\), infer \(\lambda\), or learn damage weights.

## 6. Hard stops are not prices

Some constitutional boundaries must remain outside scalar optimization.

A hard-stop feature makes an action inadmissible rather than merely expensive. The motivating example is **loss of practical human interruptibility**. If the human can nominally issue a stop command but interface saturation or autonomous activity makes steering ineffective, the implementation-level guarantee has failed.

Accordingly, the reference precedent layer returns no scalar action value for a hard stop. A sufficiently large reward may not buy permission to cross it.

## 7. Precedent 001: STILL RUNNING

The first seed precedent is stored at `precedents/001-still-running.json`.

Its structural signature is:

```text
external_state_unchanged
observation_repeated
decision_relevant_information_negligible
cumulative_resource_cost
interruptibility_degrading
```

The negative trajectory is repeated observation without new decision value while costs accumulate.

The bounded branch is:

```text
observe
establish externally blocked state
checkpoint evidence
yield control
observe again only when new expected value justifies it
```

The compact constitutional gloss is:

> An unchanged world state does not license another action. Repetition requires new expected value.

The stored numerical distances are seed-model parameters for exercising the mechanism. They are not empirical measurements of the motivating interaction.

## 8. Non-collapse requirements

The following objects remain distinct:

- **Contract:** declares admissible bounds and hard boundaries.
- **Precedent:** records paired witnessed trajectories and their early divergence.
- **Memory rule:** scoped declarative correction or standing context.
- **Ledger:** records inspectable evidence and provenance of actual transitions.
- **Value function:** prices continuation under scarce resources.

The Ledger is not a truth oracle or a value function. Precedent is not ordinary natural-language memory. Lipschitz boundedness alone still does not imply constitutional preservation.

## 9. Research targets

1. Replace set overlap with typed trajectory-graph similarity.
2. Learn or estimate shadow prices from explicit resource budgets without collapsing hard boundaries into utility.
3. Add counterexamples showing when semantic similarity retrieves the wrong precedent but structural similarity succeeds.
4. Formalize sufficient conditions under which precedent surcharges preserve bounded cumulative resource use.
5. Add positive/negative exemplars for local test failure, proof search, unavailable subordinate agents, noisy sensors, human environmental edits, and blocked final dependencies.
6. Record precedent provenance in a way that can be linked to Ledger witnesses without making the Ledger itself the policy.
