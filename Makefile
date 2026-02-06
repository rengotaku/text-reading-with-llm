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
TOC_START_PAGE ?= 15
DATA_DIR ?= data/72a2534e9e81

LLM_MODEL ?= gpt-oss:20b

.PHONY: help setup setup-voicevox run run-simple toc organize test clean clean-all gen-dict

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

run: ## Run TTS pipeline with chapter splitting
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.pipeline "$(INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED) --generate-toc --toc-start-page $(TOC_START_PAGE)

run-simple: ## Run TTS pipeline without chapter splitting
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.pipeline "$(INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED)

toc: ## Generate TOC JSON for input file
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.toc_extractor "$(INPUT)" --group-chapters --start-page $(TOC_START_PAGE) -o $(DATA_DIR)/toc.json

organize: ## Organize existing pages into chapter folders
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.organize_chapters $(DATA_DIR)

test:
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v

gen-dict:
	PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(INPUT)" --model "$(LLM_MODEL)" --merge

clean: ## Remove generated audio files (keep venv and dictionaries)
	find $(OUTPUT) -name "*.wav" -delete 2>/dev/null || true
	find $(OUTPUT) -name "cleaned_text.txt" -delete 2>/dev/null || true
	find $(OUTPUT) -type d -name "pages" -empty -delete 2>/dev/null || true

clean-all: clean ## Remove output, venv, and voicevox
	rm -rf $(VENV) $(VOICEVOX_DIR)
