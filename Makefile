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

.PHONY: help setup setup-dev setup-voicevox gen-dict xml-tts test coverage lint format clean clean-all

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Setup ---

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

setup-dev: $(VENV)/bin/activate ## Install dev dependencies + pre-commit hooks
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/pre-commit install

# --- Pipeline (gen-dict → xml-tts) ---

gen-dict: ## Generate reading dictionary with LLM (INPUT=file)
	PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(INPUT)" --model "$(LLM_MODEL)" --merge

xml-tts: ## Run XML to TTS pipeline (INPUT=file)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.xml2_pipeline -i "$(INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED)

# --- Quality ---

test: ## Run tests
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v

coverage: ## Run tests with coverage report
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run ruff linter and format check
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

format: ## Auto-format code with ruff
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

# --- Cleanup ---

clean: ## Remove generated audio files (keep venv and dictionaries)
	find $(OUTPUT) -name "*.wav" -delete 2>/dev/null || true
	find $(OUTPUT) -name "cleaned_text.txt" -delete 2>/dev/null || true
	find $(OUTPUT) -type d -name "pages" -empty -delete 2>/dev/null || true

clean-all: clean ## Remove output, venv, and voicevox
	rm -rf $(VENV) $(VOICEVOX_DIR)
