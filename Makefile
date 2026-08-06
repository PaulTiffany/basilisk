.PHONY: project test eval validate example formal paper clean package-check

project:
	python3 scripts/validate_project.py

test:
	python3 -m unittest discover -s tests -v

eval:
	PYTHONPATH=src python3 scripts/run_reference_evals.py

validate:
	python3 scripts/validate_json.py

example:
	PYTHONPATH=src python3 examples/finite_controller.py
	python3 examples/finite_quartet.py

formal:
	cd formal && lake build

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package-check: project test eval validate example

clean:
	cd paper && latexmk -C
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
