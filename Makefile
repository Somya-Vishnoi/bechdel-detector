PYTHON = PYTHONPATH=src .venv/bin/python
PYTEST = PYTHONPATH=src .venv/bin/pytest
BECHDEL = PYTHONPATH=src .venv/bin/python -m bechdel.cli

.PHONY: help all data features train evaluate report test lint clean

help:
	@echo "Bechdel Test Detector Makefile targets:"
	@echo "  make all        - Run complete end-to-end pipeline"
	@echo "  make data       - Ingest, download, and match datasets"
	@echo "  make features   - Extract dialogue and metadata features"
	@echo "  make train      - Train regression and classification models"
	@echo "  make evaluate   - Evaluate detector, hypothesis tests, and fairness"
	@echo "  make report     - Generate figures and populated reports/REPORT.md"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make clean      - Clean cache and generated test files"

all:
	$(BECHDEL) all

data:
	$(BECHDEL) data

features:
	$(BECHDEL) features

train:
	$(BECHDEL) train

evaluate:
	$(BECHDEL) evaluate

report:
	$(BECHDEL) report

test:
	$(PYTEST) -v tests/

clean:
	rm -rf __pycache__ src/bechdel/__pycache__ .pytest_cache
