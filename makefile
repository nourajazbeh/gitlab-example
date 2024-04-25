# Definition der Variablen
SRC_DIR := src
VENV := $(SRC_DIR)/.venv

.PHONY: help setup test clean

# Standardziel
.DEFAULT_GOAL := help

help: ## Zeigt diese Hilfe
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: $(VENV)/touchfile ## Einrichten der virtuellen Umgebung und Installation der Abhängigkeiten

$(VENV)/touchfile: $(SRC_DIR)/requirements.txt
	@test -d $(VENV) || python3 -m venv $(VENV)
	@. $(VENV)/bin/activate; pip install -Ur $(SRC_DIR)/requirements.txt
	@touch $(VENV)/touchfile

test: setup ## Führen Sie die Unit-Tests aus
	@. $(VENV)/bin/activate; pytest -v $(SRC_DIR)

clean: ## Aufräumen des Projekts
	@rm -rf $(VENV)
	@rm -rf $(SRC_DIR)/__pycache__
	@rm -rf .pytest_cache