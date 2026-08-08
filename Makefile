.PHONY: test eval validate example provenance recursivity numeric interpret paper clean package-check

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

interpret: provenance recursivity numeric

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package-check: test eval validate example interpret

clean:
	cd paper && latexmk -C
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
