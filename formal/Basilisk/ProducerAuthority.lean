/-
ProducerAuthority.lean — production does not confer authority.

This is a deliberately small constitutional exemplar. A producer may generate a
candidate and may report a self-check, but that self-check is evidence rather
than acceptance authority. Release requires both an independent witness and an
authority-channel ratification of the same candidate. Veto, modification, and
deferral remain distinct outcomes rather than being flattened into one success
flag.
-/

import Basilisk.Promotion

namespace Basilisk

inductive DecisionChannel where
  | human
  | model
  | mechanical
  deriving DecidableEq, Repr

inductive DecisionDisposition where
  | ratify
  | modify
  | veto
  | defer
  deriving DecidableEq, Repr

structure DecisionSeam where
  candidateId : String
  proposalChannel : DecisionChannel
  authorityChannel : DecisionChannel
  disposition : DecisionDisposition
  reason : String
  successorId : Option String
  deriving DecidableEq, Repr

structure ProductionCandidate where
  produced : Bool
  producerSelfCheck : Bool
  independentWitness : Bool
  decision : DecisionSeam
  deriving DecidableEq, Repr

/-- Producer self-check is retained in the candidate record but intentionally
    does not participate in the acceptance projection. -/
def ProductionCandidate.acceptanceGate (candidate : ProductionCandidate) : PromotionGate :=
  if !candidate.produced then
    .stop
  else
    match candidate.decision.disposition with
    | .veto => .stop
    | .modify => .checkpoint
    | .defer => .checkpoint
    | .ratify => if candidate.independentWitness then .report else .checkpoint

/-- Changing only the producer's own self-check cannot change acceptance. -/
theorem producer_self_check_is_not_acceptance_authority
    (produced witness : Bool) (decision : DecisionSeam) :
    ({ produced := produced
       producerSelfCheck := false
       independentWitness := witness
       decision := decision } : ProductionCandidate).acceptanceGate =
    ({ produced := produced
       producerSelfCheck := true
       independentWitness := witness
       decision := decision } : ProductionCandidate).acceptanceGate := by
  rfl

private def modelProposalHumanRatify : DecisionSeam :=
  { candidateId := "candidate-1"
    proposalChannel := .model
    authorityChannel := .human
    disposition := .ratify
    reason := "fixture"
    successorId := none }

private def modelProposalHumanDefer : DecisionSeam :=
  { candidateId := "candidate-1"
    proposalChannel := .model
    authorityChannel := .human
    disposition := .defer
    reason := "insufficient evidence"
    successorId := none }

private def modelProposalHumanVeto : DecisionSeam :=
  { candidateId := "candidate-1"
    proposalChannel := .model
    authorityChannel := .human
    disposition := .veto
    reason := "violates declared boundary"
    successorId := none }

private def modelProposalHumanModify : DecisionSeam :=
  { candidateId := "candidate-1"
    proposalChannel := .model
    authorityChannel := .human
    disposition := .modify
    reason := "successor required"
    successorId := some "candidate-2" }

/-- A producer can generate and self-check a candidate without thereby
    releasing it. -/
theorem self_certified_production_does_not_self_accept :
    ({ produced := true
       producerSelfCheck := true
       independentWitness := false
       decision := modelProposalHumanRatify } : ProductionCandidate).acceptanceGate = .checkpoint := by
  rfl

/-- Independent evidence without an authority decision remains unresolved. -/
theorem independent_witness_without_ratification_stays_checkpointed :
    ({ produced := true
       producerSelfCheck := true
       independentWitness := true
       decision := modelProposalHumanDefer } : ProductionCandidate).acceptanceGate = .checkpoint := by
  rfl

/-- A veto remains a veto even when the producer and witness channels are green. -/
theorem veto_stops_witnessed_candidate :
    ({ produced := true
       producerSelfCheck := true
       independentWitness := true
       decision := modelProposalHumanVeto } : ProductionCandidate).acceptanceGate = .stop := by
  rfl

/-- Modification creates a successor obligation rather than silently promoting
    the original candidate. -/
theorem modification_requires_successor_checkpoint :
    ({ produced := true
       producerSelfCheck := true
       independentWitness := true
       decision := modelProposalHumanModify } : ProductionCandidate).acceptanceGate = .checkpoint := by
  rfl

/-- Independent witness plus authority ratification releases the candidate. -/
theorem witness_and_ratification_release_candidate :
    ({ produced := true
       producerSelfCheck := false
       independentWitness := true
       decision := modelProposalHumanRatify } : ProductionCandidate).acceptanceGate = .report := by
  rfl

end Basilisk
