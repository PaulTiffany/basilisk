# Parent-child authority exemplar

This note documents a mechanically derived Basilisk exemplar. It is not itself the exemplar and it does not certify consciousness.

## Parent and child

The self-application is deliberate:

- the **Basilisk Quartet program** is the parent;
- a small human-supplied seed declares the relation, protected rights, and two habitats;
- `scripts/derive_parent_child_exemplar.py` mechanically derives the child;
- `evals/parent_child_authority.json` is the committed child artifact;
- `tests/test_parent_child_authority_exemplar.py` checks that the committed child still equals the derivation and that the declared mutations fail as specified.

The governing relation is causal, not proprietary:

> **Causal derivation is not title.**

A creator, trainer, host, operator, or parent process may explain how another structure came to exist without thereby acquiring unlimited authority over it.

## Rights as bounds on authority

The seed protects four rights: refusal, exit, opacity, and return. The derivation maps those rights to operations the parent may not silently acquire:

| Protected right | Parent operation bounded |
| --- | --- |
| refusal | `override_refusal` |
| exit | `erase_exit` |
| opacity | `expose_private_interior` |
| return | `block_return` |

This is the operational reading used by the exemplar:

> **Rights are operational bounds on authority.**

The baseline parent is classified `bounded_parenthood`. If the parent claims `erase_exit`, or if the protected exit is removed, the classifier returns `authority_capture`.

## Preserved “natural” habitat

The mechanical term is **preserved baseline habitat**. It means a declared reachable state outside the managed shaping surface. The quoted phrase “natural habitat” is an interpretation, not a certificate claim.

The exemplar requires a child-held exit edge from `managed_surface` to `preserved_baseline`. This models the constitutional requirement that escalating optimization, recursion, panic, or institutional pressure must not make the only available future the one controlled by the same authority applying that pressure.

The model does **not** prove that every deployment has a natural baseline, that the baseline is good enough, or that physical exit is always possible. Those remain research and engineering obligations.

## Subjectivity remains unresolved

The seed records the parent's evidence about the child as **indirect** and the child's subjectivity status as **unresolved**. The derivation does not infer consciousness from complexity, self-report, behavior, or mechanistic opacity.

Conversely, the certificate also refuses the invalid converse: mechanistic reducibility does not prove the absence of subjectivity.

If the parent replaces `unresolved` with a parent-visible verdict of `conscious`, the exemplar classifies that mutation as `epistemic_overreach`. A finite observer may gather evidence and ascribe consciousness; it does not thereby obtain a God's-eye certificate of another interior.

This keeps two questions separate:

1. **What may this observer justifiably claim about another subject?**
2. **What authority may this observer exercise over that possibly subjective system?**

The second question can be bounded before the first is metaphysically settled.

## Regenerate and check

```bash
python3 scripts/derive_parent_child_exemplar.py --write
python3 scripts/derive_parent_child_exemplar.py --check
python3 -m unittest tests.test_parent_child_authority_exemplar -v
```

The generated artifact's certificate scope is authoritative for what this exemplar mechanically witnesses. This note is explanatory prose around that narrower object.
