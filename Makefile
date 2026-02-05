SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Load defaults from config.yaml (overridable via: make run INPUT="..." SPEAKER="...")
CFG = grep '^$(1):' config.yaml | head -1 | sed 's/^[^:]*: *//' | sed 's/^"//;s/"$$//'

INPUT ?= $(shell $(call CFG,input))
OUTPUT ?= $(shell $(call CFG,output))
TTS_MODEL ?= $(shell $(call CFG,tts_model))
SPEAKER ?= $(shell $(call CFG,speaker))
LANGUAGE ?= $(shell $(call CFG,language))
DEVICE ?= $(shell $(call CFG,device))

LLM_MODEL ?= gpt-oss:20b

.PHONY: help setup run test clean clean-all gen-dict

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: $(VENV)/bin/activate ## Create venv and install dependencies

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV) --system-site-packages
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

run: setup ## Run TTS pipeline (generate audio from markdown)
	PYTHONPATH=$(CURDIR) $(PYTHON) src/pipeline.py "$(INPUT)" -o "$(OUTPUT)" --model "$(TTS_MODEL)" --speaker "$(SPEAKER)" --language "$(LANGUAGE)" --device "$(DEVICE)"

test: setup ## Run tests
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v

gen-dict: setup ## Generate reading dictionary using LLM
	PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(INPUT)" --model "$(LLM_MODEL)" --merge

clean: ## Remove output files (keep venv)
	rm -rf $(OUTPUT)

clean-all: clean ## Remove output and venv
	rm -rf $(VENV)
