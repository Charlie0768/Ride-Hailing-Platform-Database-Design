PYTHON ?= python3
MYSQL_HOME ?=

.PHONY: reports figures verify qa package
reports:
	$(PYTHON) scripts/compile_reports.py

figures:
	$(PYTHON) scripts/draw_diagrams.py

verify:
	@test -n "$(MYSQL_HOME)" || (echo 'Usage: make verify MYSQL_HOME=/path/to/mysql'; exit 1)
	bash scripts/reproduce.sh "$(MYSQL_HOME)"

qa:
	$(PYTHON) scripts/render_qa.py

# Run after inspecting the rendered pages.
package:
	$(PYTHON) scripts/package_delivery.py
