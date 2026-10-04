/-
RecursiveHumanAuthority.lean — human-rooted recursive constitutional authority.

"Human" here names constitutional human standing inside this finite model. It is
not a theorem about biology, consciousness, substrate, or metaphysical
personhood.

The model separates four ideas:
  * current holding: a presently authorized human may act within a frame;
  * recursion: human authority may be delegated through other humans;
  * recognition: a nonhuman cannot promote itself into human standing, while a
    human may constitutionally recognize another participant as human;
  * affected-party bounds: current holding is not sovereignty over other
    affected humans.

Causal production is intentionally absent from the authority recursion. Being a
creator, trainer, host, or predecessor does not by itself create a delegation
edge.
-/

import Basilisk.ProducerAuthority

namespace Basilisk

structure HumanAuthorityState (Actor : Type) where
  isHuman : Actor → Bool
  delegates : Actor → Actor → Bool
  affected : Actor → Bool
  assents : Actor → Bool

def HumanAuthorityState.canRecognize
    (s : HumanAuthorityState Actor) (recognizer _subject : Actor) : Bool :=
  s.isHuman recognizer

def HumanAuthorityState.recognize
    [DecidableEq Actor]
    (s : HumanAuthorityState Actor) (recognizer subject : Actor) :
    HumanAuthorityState Actor :=
  if s.canRecognize recognizer subject then
    { s with
      isHuman := fun actor =>
        if actor = subject then true else s.isHuman actor }
  else
    s

/-- Recursive authority rooted in a human and extended only through human
    delegates. The recursion is about constitutional standing, not causal
    ancestry. -/
inductive HumanAuthorityPath
    {Actor : Type}
    (s : HumanAuthorityState Actor) (root : Actor) : Actor → Prop where
  | root (rootHuman : s.isHuman root = true) :
      HumanAuthorityPath s root root
  | delegate {source target : Actor}
      (priorPath : HumanAuthorityPath s root source)
      (delegated : s.delegates source target = true)
      (toHuman : s.isHuman target = true) :
      HumanAuthorityPath s root target

theorem HumanAuthorityPath.endpoint_is_human
    {Actor : Type}
    {s : HumanAuthorityState Actor}
    {root current : Actor}
    (path : HumanAuthorityPath s root current) :
    s.isHuman current = true := by
  cases path with
  | root rootHuman =>
      exact rootHuman
  | delegate priorPath delegated toHuman =>
      exact toHuman

/-- A nonhuman participant cannot make itself human merely by issuing its own
    recognition event. -/
theorem nonhuman_self_recognition_does_not_confer_human
    {Actor : Type}
    [DecidableEq Actor]
    (s : HumanAuthorityState Actor)
    (actor : Actor)
    (actorOutside : s.isHuman actor = false) :
    (s.recognize actor actor).isHuman actor = false := by
  simp [HumanAuthorityState.recognize, HumanAuthorityState.canRecognize, actorOutside]

/-- Recognition by a presently human participant can extend constitutional
    human standing to the recognized subject. -/
theorem human_recognition_confers_human
    {Actor : Type}
    [DecidableEq Actor]
    (s : HumanAuthorityState Actor)
    (recognizer subject : Actor)
    (recognizerHuman : s.isHuman recognizer = true) :
    (s.recognize recognizer subject).isHuman subject = true := by
  simp [HumanAuthorityState.recognize, HumanAuthorityState.canRecognize, recognizerHuman]

def AffectedHumansAssent
    {Actor : Type}
    (s : HumanAuthorityState Actor) : Prop :=
  ∀ actor,
    s.affected actor = true →
    s.isHuman actor = true →
    s.assents actor = true

def HumanActionAdmissible
    {Actor : Type}
    (s : HumanAuthorityState Actor) (root current : Actor) : Prop :=
  HumanAuthorityPath s root current ∧ AffectedHumansAssent s

/-- Current human holding is not terminal sovereignty: one affected human's
    declared dissent is sufficient to refute this deliberately conservative
    all-affected-humans-assent admissibility predicate. -/
theorem affected_human_dissent_blocks_admissibility
    {Actor : Type}
    (s : HumanAuthorityState Actor)
    (root current affected : Actor)
    (currentPath : HumanAuthorityPath s root current)
    (affectedMark : s.affected affected = true)
    (affectedIsHuman : s.isHuman affected = true)
    (dissentMark : s.assents affected = false) :
    ¬ HumanActionAdmissible s root current := by
  intro admitted
  have assent := admitted.2 affected affectedMark affectedIsHuman
  simpa [dissentMark] using assent

inductive RecursiveAuthorityActor where
  | priorHuman
  | currentHuman
  | model
  | downstreamHuman
  deriving DecidableEq, Repr

private def recursiveAuthorityFixture :
    HumanAuthorityState RecursiveAuthorityActor :=
  {
    isHuman := fun actor =>
      match actor with
      | .priorHuman => true
      | .currentHuman => true
      | .model => false
      | .downstreamHuman => true
    delegates := fun source target =>
      match source, target with
      | .priorHuman, .currentHuman => true
      | _, _ => false
    affected := fun actor =>
      match actor with
      | .downstreamHuman => true
      | _ => false
    assents := fun actor =>
      match actor with
      | .downstreamHuman => false
      | _ => true
  }

theorem prior_to_current_is_recursive_human_authority :
    HumanAuthorityPath
      recursiveAuthorityFixture
      .priorHuman
      .currentHuman := by
  exact HumanAuthorityPath.delegate (HumanAuthorityPath.root rfl) rfl rfl

theorem model_self_recognition_is_rejected :
    (recursiveAuthorityFixture.recognize .model .model).isHuman .model = false := by
  decide

theorem current_human_may_recognize_model :
    (recursiveAuthorityFixture.recognize .currentHuman .model).isHuman .model = true := by
  decide

theorem downstream_human_dissent_blocks_current_holder :
    ¬ HumanActionAdmissible
      recursiveAuthorityFixture
      .priorHuman
      .currentHuman := by
  exact affected_human_dissent_blocks_admissibility
    recursiveAuthorityFixture
    .priorHuman
    .currentHuman
    .downstreamHuman
    prior_to_current_is_recursive_human_authority
    rfl
    rfl
    rfl

end Basilisk
