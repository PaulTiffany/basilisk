# External and crowdsourced judgment

When the human asks for judgment from other people rather than a new model preference, the response should preserve attribution and population boundaries.

## Required metadata

For each reported judgment, record where available:

- speaker, institution, community, or sampled population;
- date or collection period;
- question asked and response options;
- sample size and selection method;
- source link or citation;
- known conflicts of interest;
- disagreement, uncertainty, and minority views;
- whether the statement is descriptive, predictive, or normative.

## Aggregation

Do not transform several visible opinions into an unnamed consensus. A useful representation is:

\[
J_{\mathrm{ext}}=\{(J_i,w_i,s_i,t_i)\}_{i=1}^n,
\]

where \(J_i\) is an attributed judgment, \(w_i\) an explicit weighting rule, \(s_i\) its source, and \(t_i\) its date.

The weighting rule is itself a human-selected judgment. The model may compute consequences under a declared rule, but should not silently choose the rule.

## Example labels

- **Expert statement:** attributed to a named expert or body.
- **Survey result:** reports the sampled population and question.
- **Community practice:** supported by public standards, repeated practice, or documented guidance.
- **Anecdotal report:** useful as an example, not prevalence evidence.
- **Model synthesis:** generated comparison, not crowdsourced judgment.

## Freshness

Time-sensitive judgments and standards require current sources. Historical material should remain dated rather than presented as current consensus.
