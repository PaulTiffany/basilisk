# Reading the Lean Lake

This file is the **human map** of Basilisk's Lean surface.

If the formal tree is cognitively expensive, start here. The Lean files are not
the source of the project's values and they are not a substitute for the human
frame. They are downstream witnesses that make selected distinctions precise.

## The five things to remember

1. **Human meaning comes first.** A human-supplied seed, protocol decision, or
   declared distinction is upstream of the theorem that later checks it.
2. **Lean proves only the proposition encoded.** A green theorem is not a moral
   judgment, a consciousness detector, or universal authorization.
3. **Formalization is observer-bounded.** A theorem preserves a declared view of
   a surface. It does not become a God's-eye ontology of the thing observed.
4. **Different modules answer different questions.** Contract, execution,
   coupling, evidence, authority, standing, privacy, and reachability must not
   silently collapse into one object.
5. **No theorem promotes itself into authority.** A proof can constrain what is
   rational to claim. It cannot grant itself permission to act.

## Development direction

Read the project in this direction:

```text
human distinction / seed
        |
        v
mechanical parent or protocol rule
        |
        v
derived finite artifact / executable witness
        |
        +-------------------+
        |                   |
        v                   v
Python/runtime          Lean mirror
        |                   |
        +---------+---------+
                  |
                  v
       tests / inventories / CI
                  |
                  v
          evidence for humans
```

The arrow **does not reverse**. Lean is allowed to expose a contradiction or a
bad formalization, but a theorem does not become the author of the human
constitutional frame.

## Four questions for any theorem

When you encounter a theorem name, ask:

1. **Observer:** What representation or observer is this theorem relative to?
2. **Distinction:** What two things is it preventing us from collapsing?
3. **Witness:** What finite object actually witnesses the claim?
4. **Non-claim:** What tempting larger conclusion is still *not* licensed?

If those four answers are unclear, the formal surface is not yet interpretable
enough.

## The lake by meaning

### 1. What can cross a boundary?

- **Port.lean** — gives us typed ingress/egress. It says what the declared
  interface *is*, not what the world ultimately is.
- **Contract.lean** — says which declared events are admissible.
- **Script.lean / GateProjection.lean** — mirrors the finite controller that
  maps a typed action state to Proceed / Report / Checkpoint / Stop.

**Do not infer:** that the typed action state perfectly captures natural
language, hidden intent, or every affected party.

### 2. Who may authorize what?

- **Authority.lean** — structured standing permission before it is collapsed to
  an authorization bit.
- **AuthorityAlgebra.lean** — keeps permission breadth separate from freshness.
- **AuthorityVectors.lean** — finite cross-checks for structured authority.
- **ProducerAuthority.lean** — producer, witness, and human acceptance authority
  remain distinct. A model or mechanical ratification does not become human
  acceptance authority.
- **RecursiveHumanAuthority.lean** — makes the human root explicit without
  turning the current human holder into a terminal sovereign.

The recursive human-authority slice currently says, in a deliberately finite
model:

```text
prior human standing
        |
      delegates
        v
current human holder
        |
        +---- may recognize new human standing
        |
        +---- is still bounded by affected humans
```

A nonhuman cannot create its own human standing merely by self-recognition.
Human recognition can extend constitutional human standing. Delegation preserves
human endpoints. A current holder remains bounded by represented affected-human
standing.

**Do not infer:** that one human speaks for every human, that unanimity is the
final governance rule, that biology exhausts personhood, or that Lean has solved
collective legitimacy.

### 3. What can we know from a trace?

- **Ledger.lean** — records can be encoded and linked without loss inside the
  declared model.
- **LedgerSemantics.lean** — a structurally valid record can still carry a false
  claim.
- **Counterexamples.lean** — the same visible Ledger trace can be compatible
  with different hidden Scripts.

This is the anti-oracle rule for provenance:

> A record can preserve evidence without becoming the truth of everything that
> caused it.

### 4. What counts as a boundary or coupling?

- **Blanket.lean** — finite separator shape only.
- **DependencyCut.lean / DependencyMutationWitness.lean** — which declared
  dependency relations enter a local family closure and how a topology mutation
  can change that closure.
- **Observability.lean** — external observability does not imply total access to
  relevant interior state.
- **Privacy.lean** — useful accountability need not require total disclosure.

**Do not infer:** that the current finite Blanket proves Fristonian dynamics,
Bayesian conditional independence, or a metaphysical inside/outside.

### 5. What survives transformation?

- **WitnessAlgebra.lean** — makes transports and commuting witnesses explicit.
- **ConstitutionalLipschitz.lean / LipschitzWitness.lean** — smoothness alone
  does not preserve a constitutional predicate.
- **StagingGeometry.lean** — declared observational distinctions may refine as
  the frame changes.
- **ParameterizedTime.lean** — finite observer-history can induce an operational
  arrow under explicit assumptions.
- **AssumptionSurfaces.lean / AssumptionNecessity.lean** — show which proof
  assumptions are actually load-bearing.

This family is especially important for avoiding the mistake:

```text
mathematically smooth  !=  constitutionally acceptable
```

### 6. What futures remain available?

- **Reachability.lean** — compares reachable futures relative to a declared
  transition relation.
- **Evitability.lean** — nominal alternatives need not be materially viable.
- **Play.lean** — bounded play must preserve escape/correction structure.
- **ProtectedTen.lean / HorizonGeometry.lean** — finite witnesses about retained
  distinctions under declared growth and horizon constructions.

**Do not infer:** a universal utility function or a globally correct future.

### 7. What becomes shared?

- **Materiality.lean** — finite shared-obstruction and recursive-materialization
  witnesses.
- **Promotion.lean** — imagination, hypothesis, shared assertion, authorized
  action, and enactment do not silently promote into one another.

This is where observer-boundedness matters most. A shared witness can justify a
stronger shared claim without converting every local representation into one
universal ontology.

## Authority: the current picture in one screen

```text
CAPABILITY
    |
    | does not imply
    v
AUTHORITY

PRODUCTION ----> evidence
SELF-CHECK ----> evidence
WITNESS --------> evidence

human ratification + required witness
              |
              v
       accepted candidate

human authority itself is recursive:
prior humans -> current holder -> future/affected humans

and none of these arrows means ownership:
causal derivation != title
```

The current human at the interface is therefore a **holder of a frame**, not the
uncaused source of all legitimacy.

## Observer-bound agency

Basilisk should not require one universal object to contain every legitimate
meaning of "agent" at once.

A useful reading discipline is to treat agency claims as indexed by an observer
and a contact surface:

```text
Agency(observer, subject, surface)
```

Different observers may have different legitimate partial witnesses. A local
grant of agency, standing, authorship, or authority does not silently become a
universal grant. Conversely, failure of one observer to witness a property does
not prove the property's universal absence.

This is a reading rule for the present formal work, not yet a universal Lean
theorem of agency.

## When a Lean theorem should stop you

A theorem should change the project when it reveals that:

- two concepts we intended to separate have been encoded as the same thing;
- a stated invariant does not follow from its declared assumptions;
- a mechanically derived artifact disagrees with the formal mirror;
- an assumption we treated as decorative is actually load-bearing;
- an allegedly harmless generalization creates states the human seed never
  authorized.

That is Lean serving the project rather than ruling it.

## When Lean should *not* decide

Lean should not be asked to settle, by itself:

- whether a system is conscious;
- who counts as human in the lived or metaphysical sense;
- whose suffering matters;
- whether a current institutional arrangement is morally legitimate;
- whether one observer's representation exhausts another observer;
- whether a formally valid action should be enacted in the world.

Those are not failures of formalization. They are boundaries on what this
formalization presently claims.

## Practical navigation

If you are reading under high cognitive load:

1. Read this file.
2. Read the relevant human/protocol document.
3. Open **one** Lean module only.
4. Find the theorem named in the documentation.
5. Read its comment and statement before its proof.
6. Check the registered non-claim before generalizing it.

For authority work right now, the shortest path is:

```text
docs/human-authority-boundary.md
        ->
docs/producer-authority-separation.md
        ->
formal/Basilisk/ProducerAuthority.lean
        ->
formal/Basilisk/RecursiveHumanAuthority.lean
```

Everything else can wait until it becomes relevant.
