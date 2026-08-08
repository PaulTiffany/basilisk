/-
Basilisk — the finite combinatorial core of the Basilisk Quartet
(Contract/TTDC, Script/TTIE, Blanket/TTCS, Ledger/TTPR), following
`formal/README.md`'s plan: "the probabilistic and metric versions
should follow the finite combinatorial core, rather than being
axiomatized prematurely."

Verified here (core Lean 4 + decidable/classical reasoning only, no
mathlib dependency):
  * Port.lean             — typed ports, Ω_p = I_p × O_p
  * Contract.lean         — admissible-event predicate, trace lifting
  * Script.lean           — finite mirror of gate-relevant Python state/law
  * Authority.lean        — structured standing authority before Boolean projection
  * AuthorityVectors.lean — mechanically transcribed structured authority corpus
  * AuthorityAlgebra.lean — permission breadth and authorization-freshness joins
  * ControllerVectors.lean — shared Python/Lean observable gate vectors
  * WitnessAlgebra.lean   — typed transports, loss classes, commuting squares
  * LipschitzWitness.lean — shared JSON/NumPy/Lean counterexample instance
  * StagingGeometry.lean  — frame-indexed refinement and scale-invariant zero kernels
  * ParameterizedTime.lean — reflective history arrow and amortized parameter transport
  * AssumptionSurfaces.lean — countermodels for dropped composition hypotheses
  * AssumptionNecessity.lean — countermodels for substantive theorem premises
  * JunctionTopology.lean — three-way interaction signatures and controls
  * Promotion.lean        — imagination/verification/authority promotion boundaries
  * Materiality.lean      — shared obstruction and recursive materialization witnesses
  * Evitability.lean      — nominal choice versus materially viable alternatives
  * Blanket.lean          — direct-edge separator-property shape
  * DependencyCut.lean    — parent/child/co-parent family closure
  * DependencyMutationWitness.lean — shared topology-mutation instance
  * Ledger.lean           — lossless encode/decode and chain discipline
  * LedgerSemantics.lean  — structural integrity does not entail semantic truth
  * Quartet.lean          — bundles the four as distinct fields
  * Counterexamples.lean  — Script/Ledger non-identifiability witness
  * Reachability.lean     — hypothesis-relative reachable-future monotonicity
  * ConstitutionalLipschitz.lean — geometric/constitutional separation
-/

import Basilisk.Port
import Basilisk.Contract
import Basilisk.Script
import Basilisk.Authority
import Basilisk.AuthorityVectors
import Basilisk.AuthorityAlgebra
import Basilisk.ControllerVectors
import Basilisk.WitnessAlgebra
import Basilisk.ConstitutionalLipschitz
import Basilisk.LipschitzWitness
import Basilisk.StagingGeometry
import Basilisk.ParameterizedTime
import Basilisk.AssumptionSurfaces
import Basilisk.AssumptionNecessity
import Basilisk.JunctionTopology
import Basilisk.Promotion
import Basilisk.Materiality
import Basilisk.Evitability
import Basilisk.Blanket
import Basilisk.DependencyCut
import Basilisk.DependencyMutationWitness
import Basilisk.Ledger
import Basilisk.LedgerSemantics
import Basilisk.Quartet
import Basilisk.Counterexamples
import Basilisk.Reachability

namespace Basilisk

#print axioms ActionGate.fromNat_toNat
#print axioms StandingAuthority.inactive_never_covers
#print axioms StandingAuthority.expired_never_covers
#print axioms StandingAuthority.external_effect_requires_permission
#print axioms AuthorityEnvelope.covers_independent_of_provenance
#print axioms ActionIntent.current_authorization_dominates_projection
#print axioms ActionIntent.assessWithStanding_eq_assess_projection
#print axioms standing_authority_does_not_replace_fresh_high_scope_authorization
#print axioms authority_vectors_hold
#print axioms RiskLevel.le_max_left
#print axioms RiskLevel.le_max_right
#print axioms PermissionProfile.le_join_left
#print axioms PermissionProfile.le_join_right
#print axioms PermissionProfile.covers_mono
#print axioms PermissionProfile.join_preserves_left_coverage
#print axioms PermissionProfile.join_preserves_right_coverage
#print axioms AuthorityBasis.join_comm
#print axioms AuthorityBasis.join_assoc
#print axioms AuthorityBasis.join_idem
#print axioms AuthorityBasis.standing_join_current
#print axioms AuthorityBasis.none_join_standing
#print axioms controller_vectors_hold
#print axioms CommutesSquare.identity
#print axioms CommutesSquare.postcompose
#print axioms shared_lipschitz_counterexample
#print axioms zeroKernel_refines_of_pointwise_le
#print axioms positive_scale_preserves_zeroKernel
#print axioms added_component_refines_zeroKernel
#print axioms fixture_strict_refinement
#print axioms operationalTime_reflectiveStep
#print axioms reflectiveStep_no_historyMonotone_undo
#print axioms reversible_world_does_not_remove_reflective_arrow
#print axioms amortized_parameter_compilation_fixture
#print axioms preserves_comp_needs_hT
#print axioms preserves_comp_needs_hS
#print axioms AssumptionNecessity.blanket_without_no_edges_can_fail
#print axioms AssumptionNecessity.reachable_without_relation_inclusion_can_fail
#print axioms AssumptionNecessity.postcompose_without_commuting_square_can_fail
#print axioms AssumptionNecessity.covers_mono_without_profile_order_can_fail
#print axioms AssumptionNecessity.covers_mono_without_source_coverage_can_fail
#print axioms AssumptionNecessity.join_without_source_coverage_can_fail
#print axioms AssumptionNecessity.zeroKernel_refinement_without_monotonicity_can_fail
#print axioms AssumptionNecessity.zeroKernel_without_zero_premise_can_fail
#print axioms AssumptionNecessity.zero_scale_does_not_preserve_zeroKernel
#print axioms AssumptionNecessity.history_monotonicity_is_load_bearing
#print axioms tj01TrefoilWitness
#print axioms tj01StopReleaseWitness
#print axioms uc01UnknotWitness
#print axioms dc01DetachedWitness
#print axioms recurrence_does_not_confer_verification
#print axioms ideal_does_not_confer_verification
#print axioms recurrence_does_not_confer_authority
#print axioms ideal_cannot_self_authorize
#print axioms verification_releases_assertion
#print axioms human_authorization_releases_action
#print axioms wall_shared_obstruction
#print axioms shared_belief_not_obstruction
#print axioms bridge_recursive_materialization
#print axioms nominal_choice_does_not_imply_evitability
#print axioms plural_identity_preserves_evitability
#print axioms Contract.traceAdmissible_tail
#print axioms Blanket.isSeparator_of_no_edges
#print axioms DepGraph.familyClosure_iff
#print axioms dependency_mutation_adds_coparent
#print axioms LedgerEntry.decode_encode
#print axioms chained_does_not_entail_claim_truth
#print axioms lossless_record_does_not_entail_claim_truth
#print axioms scriptHonest_ne_scriptSneaky
#print axioms ledger_does_not_identify_script
#print axioms reachable_mono
#print axioms lipschitz_alone_not_constitutional
#print axioms PreservesPredicate.comp

end Basilisk
