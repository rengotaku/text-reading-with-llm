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

BOOK_DIR ?= $(shell $(call CFG,book_dir))
OUTPUT ?= $(shell $(call CFG,output))

# Derive input file path from BOOK_DIR
BOOK_INPUT := $(BOOK_DIR)/book.xml
STYLE_ID ?= 13
SPEED ?= 1.0
ACCELERATION_MODE ?= AUTO
MAX_LENGTH ?= 300

LLM_MODEL ?= gpt-oss:20b
DRY_RUN ?=
VERBOSE ?=

# Convert DRY_RUN to --dry-run flag
DRY_RUN_FLAG := $(if $(DRY_RUN),--dry-run,)
VERBOSE_FLAG := $(if $(VERBOSE),--verbose,)

# === Help & Setup ===
.PHONY: help guide setup setup-dev setup-voicevox reset-vvm

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

guide: setup ## Interactive setup guide (recommended for first-time users)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.setup_guide

# === Setup ===

setup: $(VENV)/bin/activate setup-voicevox ## Create venv and install all dependencies

$(VENV)/bin/activate: pyproject.toml
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PIP) install https://github.com/VOICEVOX/voicevox_core/releases/download/$(VOICEVOX_VERSION)/$(VOICEVOX_WHEEL)
	touch $(VENV)/bin/activate

setup-voicevox: $(VOICEVOX_DIR)/onnxruntime/lib ## Download VOICEVOX models and runtime

$(VOICEVOX_DIR)/onnxruntime/lib:
	@echo "Downloading VOICEVOX Core files..."
	wget -q https://github.com/VOICEVOX/voicevox_core/releases/download/$(VOICEVOX_VERSION)/$(VOICEVOX_DOWNLOADER)
	chmod +x $(VOICEVOX_DOWNLOADER)
	./$(VOICEVOX_DOWNLOADER) --output $(VOICEVOX_DIR)
	rm -f $(VOICEVOX_DOWNLOADER)

reset-vvm: ## Re-download VVM files (fixes version mismatch warnings)
	@echo "Removing existing VVM files..."
	rm -rf $(VOICEVOX_DIR)/models/vvms/
	rm -rf $(VOICEVOX_DIR)/onnxruntime/lib
	@echo "Re-downloading VOICEVOX Core files..."
	$(MAKE) setup-voicevox

setup-dev: $(VENV)/bin/activate ## Install dev dependencies + pre-commit hooks
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/pre-commit install

# === Pipeline (gen-dict → xml-tts) ===
.PHONY: gen-dict clean-text xml-tts run

gen-dict: ## Generate reading dictionary with LLM (BOOK_DIR=dir)
	PYTHONPATH=$(CURDIR) $(PYTHON) src/generate_reading_dict.py "$(BOOK_INPUT)" --model "$(LLM_MODEL)" --merge $(DRY_RUN_FLAG)

clean-text: ## Generate cleaned_text.txt from XML (BOOK_DIR=dir)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.text_cleaner_cli -i "$(BOOK_INPUT)" -o "$(OUTPUT)" $(DRY_RUN_FLAG)

xml-tts: ## Run XML to TTS pipeline (BOOK_DIR=dir)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.xml_pipeline -i "$(BOOK_INPUT)" -o "$(OUTPUT)" --style-id $(STYLE_ID) --speed $(SPEED) $(DRY_RUN_FLAG)

run: gen-dict clean-text xml-tts ## Run full pipeline: dict → clean-text → TTS (BOOK_DIR=dir)

# === Dialogue Pipeline ===
# Helper to get content hash from BOOK_INPUT file
CONTENT_HASH = $(shell PYTHONPATH=$(CURDIR) $(PYTHON) -c "from src.dict_manager import get_xml_content_hash; from pathlib import Path; print(get_xml_content_hash(Path('$(BOOK_INPUT)')))" 2>/dev/null)
HASH_DIR = $(OUTPUT)/$(CONTENT_HASH)

.PHONY: dialogue-convert dialogue-split dialogue-tts dialogue

dialogue-convert: ## Convert book XML to dialogue form with LLM (BOOK_DIR=dir)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.dialogue_converter -i "$(BOOK_INPUT)" -o "$(OUTPUT)" --model "$(LLM_MODEL)" $(DRY_RUN_FLAG)

dialogue-split: ## Split long texts in dialogue XML for TTS (MAX_LENGTH=300)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.dialogue_text_splitter -i "$(HASH_DIR)/dialogue_book.xml" --max-length $(MAX_LENGTH)

dialogue-tts: ## Generate multi-speaker TTS from dialogue XML (ACCELERATION_MODE=AUTO|CPU|GPU)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m src.dialogue_pipeline -i "$(HASH_DIR)/dialogue_book.xml" -o "$(OUTPUT)" --acceleration-mode "$(ACCELERATION_MODE)" --dict-source "$(BOOK_INPUT)" $(DRY_RUN_FLAG) $(VERBOSE_FLAG)

dialogue: dialogue-convert dialogue-split gen-dict clean-text dialogue-tts ## Run full dialogue pipeline

# === Demo & Verification ===
.PHONY: demo-coverage

demo-coverage: ## Demo keyword extraction and coverage validation
	PYTHONPATH=$(CURDIR) $(PYTHON) scripts/demo_coverage.py

# === Quality ===
.PHONY: test coverage lint format

test: ## Run tests
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v

coverage: ## Run tests with coverage report (threshold: 70%)
	PYTHONPATH=$(CURDIR) $(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=70

lint: ## Run ruff linter, format check, and mypy
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy src/

format: ## Auto-format code with ruff
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

# === Cleanup ===
.PHONY: clean clean-all

clean: ## Remove generated audio files (keep venv and dictionaries)
	@test -n "$(OUTPUT)" || { echo "Error: OUTPUT is empty, refusing to run find on root"; exit 1; }
	find $(OUTPUT) -name "*.wav" -delete 2>/dev/null || true
	find $(OUTPUT) -name "cleaned_text.txt" -delete 2>/dev/null || true
	find $(OUTPUT) -type d -name "pages" -empty -delete 2>/dev/null || true

clean-all: clean ## Remove output, venv, and voicevox
	rm -rf $(VENV) $(VOICEVOX_DIR)
