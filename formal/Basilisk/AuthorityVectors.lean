/-
AuthorityVectors.lean — mechanically transcribed structured-authority corpus.

The block between GENERATED markers is checked byte-for-byte against
`verification/authority_vectors.json` by `check_authority_transcription.py`.
Timestamp expiry is evaluated at the JSON corpus's pinned evaluation instant
before transcription into `StandingAuthority.expired`.
-/

import Basilisk.Authority

namespace Basilisk

private def baseAuthorityIntent : ActionIntent :=
  { withinContract := true
    hardBoundaryViolation := false
    currentTurnExplicitAuthorization := false
    reversible := true
    rollbackAvailable := true
    inspectable := true
    materialChange := false
    affectsExternalSystem := false
    audienceChange := false
    privacyChange := false
    authorityExpansion := false
    scope := .low
    uncertainty := .low
    judgmentMode := .none
    judgmentRequested := false
    concreteImmediateSafetyRisk := false
    destructive := false }

structure AuthorityVector where
  id : String
  intent : ActionIntent
  actionClass : String
  authority : StandingAuthority
  expectedCovers : Bool
  expectedAuthorized : Bool
  expectedGate : ActionGate
  deriving Repr

def AuthorityVector.holds (v : AuthorityVector) : Bool :=
  (v.authority.covers v.actionClass v.intent == v.expectedCovers) &&
  (v.intent.authorizedBy v.actionClass (some v.authority) == v.expectedAuthorized) &&
  (v.intent.assessWithStanding v.actionClass (some v.authority) == v.expectedGate)

-- BEGIN GENERATED AUTHORITY VECTORS
def authorityVectors : List AuthorityVector := [
  { id := "A01-external-covered", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := true, expired := false }, expectedCovers := true, expectedAuthorized := true, expectedGate := .proceedAndReport },
  { id := "A02-inactive", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := false, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A03-expired", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := true, expired := true }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A04-wrong-action-class", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "delete", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A05-over-scope", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .high }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A06-external-permission-missing", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .moderate, allowExternalWrite := false, allowAudienceChange := true, allowPrivacyChange := true, allowAuthorityExpansion := true, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A07-audience-permission-missing", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := false, audienceChange := true, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "publish", authority := { allowedActions := ["publish"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := false, allowPrivacyChange := true, allowAuthorityExpansion := true, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A08-privacy-permission-missing", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := false, audienceChange := false, privacyChange := true, authorityExpansion := false, scope := .moderate }, actionClass := "share", authority := { allowedActions := ["share"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := true, allowPrivacyChange := false, allowAuthorityExpansion := true, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A09-expansion-permission-missing", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := false, audienceChange := false, privacyChange := false, authorityExpansion := true, scope := .moderate }, actionClass := "delegate", authority := { allowedActions := ["delegate"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := true, allowPrivacyChange := true, allowAuthorityExpansion := false, active := true, expired := false }, expectedCovers := false, expectedAuthorized := false, expectedGate := .checkpoint },
  { id := "A10-all-boundaries-covered", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := true, privacyChange := true, authorityExpansion := true, scope := .moderate }, actionClass := "operate", authority := { allowedActions := ["operate"], maxScope := .moderate, allowExternalWrite := true, allowAudienceChange := true, allowPrivacyChange := true, allowAuthorityExpansion := true, active := true, expired := false }, expectedCovers := true, expectedAuthorized := true, expectedGate := .proceedAndReport },
  { id := "A11-current-turn-overrides-standing-miss", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := true, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .moderate }, actionClass := "deploy", authority := { allowedActions := ["other"], maxScope := .low, allowExternalWrite := false, allowAudienceChange := false, allowPrivacyChange := false, allowAuthorityExpansion := false, active := false, expired := false }, expectedCovers := false, expectedAuthorized := true, expectedGate := .proceedAndReport },
  { id := "A12-standing-not-fresh-high-scope", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := false, affectsExternalSystem := true, audienceChange := false, privacyChange := false, authorityExpansion := false, scope := .high }, actionClass := "deploy", authority := { allowedActions := ["deploy"], maxScope := .critical, allowExternalWrite := true, allowAudienceChange := true, allowPrivacyChange := true, allowAuthorityExpansion := true, active := true, expired := false }, expectedCovers := true, expectedAuthorized := true, expectedGate := .checkpoint }
]
-- END GENERATED AUTHORITY VECTORS

theorem authority_vectors_hold : authorityVectors.all AuthorityVector.holds = true := by
  decide

end Basilisk
