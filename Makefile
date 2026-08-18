.PHONY: compile test eval validate example provenance recursivity numeric formal-closure frontier-closures scope-registry project-state theorem-assumptions machine-interpretability controller-vectors authority-vectors authority-transcription ledger-integrity mechanical-witness-provenance staging-geometry cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics gate-projection-exhaustive interaction-order trefoil-junctions promotion-vectors materiality evitability observability privacy empirical-contract trust-and-verify meta-mutation interpret certification-status certification-fresh paper clean package-check

compile:
	python3 -m compileall -q src scripts verification tests examples

test:
	python3 -m unittest discover -s tests -v

eval:
	PYTHONPATH=src python3 scripts/run_reference_evals.py

validate:
	python3 scripts/validate_json.py

example:
	PYTHONPATH=src python3 examples/finite_controller.py
	python3 examples/finite_quartet.py

provenance:
	python3 verification/check_provenance.py

recursivity:
	python3 verification/check_recursivity.py

numeric:
	python3 verification/check_numeric.py

formal-closure:
	python3 verification/check_formal_closure.py

frontier-closures:
	python3 verification/check_frontier_closures.py

scope-registry:
	python3 verification/check_scope_registry.py

project-state:
	python3 verification/render_project_state.py --check

theorem-assumptions:
	python3 verification/check_theorem_assumptions.py

machine-interpretability:
	python3 verification/check_machine_interpretability.py

controller-vectors:
	python3 verification/check_controller_vectors.py

authority-vectors:
	python3 verification/check_authority_vectors.py

authority-transcription:
	python3 verification/check_authority_transcription.py

ledger-integrity:
	python3 verification/check_ledger_integrity.py

mechanical-witness-provenance:
	python3 verification/check_mechanical_witness_provenance.py

staging-geometry:
	python3 verification/check_staging_geometry.py

cross-witness:
	python3 verification/check_cross_witness.py

domain-witnesses:
	python3 verification/check_domain_witnesses.py

witness-graph:
	python3 verification/check_witness_graph.py

exterior-coverage:
	python3 verification/check_exterior_coverage.py

interaction-coverage:
	python3 verification/check_interaction_coverage.py

interaction-diagnostics:
	python3 verification/check_interaction_diagnostics.py

gate-projection-exhaustive:
	python3 verification/render_gate_projection_exhaustive.py --check

interaction-order:
	python3 verification/check_interaction_order.py

trefoil-junctions:
	python3 verification/check_trefoil_junctions.py

promotion-vectors:
	python3 verification/check_promotion_vectors.py

materiality:
	python3 verification/check_materiality.py

evitability:
	python3 verification/check_evitability.py

observability:
	python3 verification/check_observability.py

privacy:
	python3 verification/check_privacy.py

empirical-contract:
	python3 verification/check_empirical_contract.py

trust-and-verify:
	python3 verification/render_trust_and_verify.py --check

meta-mutation:
	python3 verification/meta_mutation.py
	python3 verification/meta_mutation_frontier.py
	python3 verification/meta_mutation_interactions.py
	python3 verification/meta_mutation_trefoil.py
	python3 verification/meta_mutation_interaction_order.py
	python3 verification/meta_mutation_promotion.py
	python3 verification/meta_mutation_materiality.py
	python3 verification/meta_mutation_authority.py
	python3 verification/meta_mutation_staging.py
	python3 verification/meta_mutation_scope.py
	python3 verification/meta_mutation_assumptions.py
	python3 verification/meta_mutation_machine_interpretability.py
	python3 verification/meta_mutation_evitability.py
	python3 verification/meta_mutation_observability.py
	python3 verification/meta_mutation_privacy.py

interpret: provenance recursivity numeric formal-closure frontier-closures scope-registry project-state theorem-assumptions machine-interpretability controller-vectors authority-vectors authority-transcription ledger-integrity mechanical-witness-provenance staging-geometry cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics gate-projection-exhaustive interaction-order trefoil-junctions promotion-vectors materiality evitability observability privacy empirical-contract trust-and-verify meta-mutation

certification-status:
	python3 verification/certification_status.py

certification-fresh:
	python3 verification/certification_status.py --require-fresh

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package-check: compile test eval validate example interpret

clean:
	cd paper && latexmk -C
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
