SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# VOICEVOX settings
VOICEVOX_DIR := voicevox_core
VOICEVOX_VERSION := 0.16.3
VOICEVOX_WHEEL := voicevox_core-$(VOICEVOX_VERSION)-cp310-abi3-manylinux_2_34_x86_64.whl
VOICEVOX_DOWNLOADER := download-linux-x64

# Load defaults from config.yaml
CFG = grep '^$(1):' config.yaml | head -1 | sed 's/^[^:]*: *//' | sed 's/^"//;s/"$$//'

INPUT ?= $(shell $(call CFG,input))
OUTPUT ?= $(shell $(call CFG,output))
STYLE_ID ?= 13
SPEED ?= 1.0

LLM_MODEL ?= gpt-oss:20b

.PHONY: help setup setup-voicevox run test clean clean-all gen-dict

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: $(VENV)/bin/activate setup-voicevox ## Create venv and install all dependencies

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install https://github.com/VOICEVOX/voicevox_core/releases/download/$(VOICEVOX_VERSION)/$(VOICEVOX_WHEEL)
	touch $(VENV)/bin/activate

setup-voicevox: $(VOICEVOX_DIR)/onnxruntime/lib ## Download VOICEVOX models and runtime

$(VOICEVOX_DIR)/onnxruntime/lib:
	@echo "Downloading VOICEVOX Core files..."
	wget -q https://github.com/VOICEVOX/voicevox_core/releases/download/$(VOICEVOX_VERSION)/$(VOICEVOX_DOWNLOADER)
	chmod +x $(VOICEVOX_DOWNLOADER)
	./$(VOICEVOX_DOWNLOADER) --output $(VOICEVOX_DIR)
	rm -f $(VOICEVOX_DOWNLOADER)

run: setup ## Run TTS pipeline (generate audio from markdown)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.pipeline "$(INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED)

test: setup ## Run tests
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v

gen-dict: setup ## Generate reading dictionary using LLM
	PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(INPUT)" --model "$(LLM_MODEL)" --merge

clean: ## Remove output files (keep venv)
	rm -rf $(OUTPUT)

clean-all: clean ## Remove output, venv, and voicevox
	rm -rf $(VENV) $(VOICEVOX_DIR)
