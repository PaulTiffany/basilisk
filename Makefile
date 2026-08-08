.PHONY: compile test eval validate example provenance recursivity numeric formal-closure controller-vectors cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics trefoil-junctions meta-mutation interpret paper clean package-check

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

controller-vectors:
	python3 verification/check_controller_vectors.py

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

meta-mutation:
	python3 verification/meta_mutation.py
	python3 verification/meta_mutation_frontier.py
	python3 verification/meta_mutation_interactions.py
	python3 verification/meta_mutation_trefoil.py

interpret: provenance recursivity numeric formal-closure controller-vectors cross-witness domain-witnesses witness-graph exterior-coverage interaction-coverage interaction-diagnostics trefoil-junctions meta-mutation

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package-check: compile test eval validate example interpret

clean:
	cd paper && latexmk -C
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
