.PHONY: compile test eval validate example provenance recursivity numeric formal-closure frontier-closures controller-vectors authority-vectors authority-transcription ledger-integrity staging-geometry cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics trefoil-junctions promotion-vectors materiality meta-mutation interpret paper clean package-check

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

controller-vectors:
	python3 verification/check_controller_vectors.py

authority-vectors:
	python3 verification/check_authority_vectors.py

authority-transcription:
	python3 verification/check_authority_transcription.py

ledger-integrity:
	python3 verification/check_ledger_integrity.py

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

trefoil-junctions:
	python3 verification/check_trefoil_junctions.py

promotion-vectors:
	python3 verification/check_promotion_vectors.py

materiality:
	python3 verification/check_materiality.py

meta-mutation:
	python3 verification/meta_mutation.py
	python3 verification/meta_mutation_frontier.py
	python3 verification/meta_mutation_interactions.py
	python3 verification/meta_mutation_trefoil.py
	python3 verification/meta_mutation_promotion.py
	python3 verification/meta_mutation_materiality.py
	python3 verification/meta_mutation_authority.py
	python3 verification/meta_mutation_staging.py

interpret: provenance recursivity numeric formal-closure frontier-closures controller-vectors authority-vectors authority-transcription ledger-integrity staging-geometry cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics trefoil-junctions promotion-vectors materiality meta-mutation

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package-check: compile test eval validate example interpret

clean:
	cd paper && latexmk -C
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
