SHELL := /bin/bash

dry-run ?= 0

ifdef retry
	RETRY_PARAM = --retry $(retry)
endif

ifeq ($(dry-run), 1)
	RUN_CMD = . .venv/bin/activate && python3 main.py --dry-run --config $(config) --input $(input) $(RETRY_PARAM) --output $(output)
else
	RUN_CMD = . .venv/bin/activate && python3 main.py --config $(config) --input $(input) $(RETRY_PARAM) --output $(output)
endif

.PHONY: help
help:
	@echo
	@echo "Makefile commands:"
	@echo "  make setup  - Set up the Python virtual environment and install dependencies."
	@echo "  make run    - Run the main Python application. Use cases:"
	@echo "      make run config=[config-file] input=[input-file] output=[output-file]"
	@echo "           Contextual translation of the input-file."
	@echo "           The config-file is a '.yaml' file that defines the translation settings."
	@echo "           The result is written to the output file."
	@echo
	@echo "      make run config=[config-file] input=[input-file] output=[output-file] retry=[retry-file]"
	@echo "           Same as the previous, but the completed translations are used from"
	@echo "             the 'retry file', which is a previous SRT result."
	@echo "           The 'failed-translation-marker' shows the failed segments. See: config file."
	@echo
	@echo "      make run dry-run=1 config=[config-file] input=[input-file] output=[output-file]"
	@echo "           Executes only the regex replacements defined in the config-file,"
	@echo "           without loading the model. (This can also have a 'retry-file' param.)"
	@echo
	@echo "  make clean  - Remove the Python virtual environment."
	@echo "  make test   - Execute the unit tests."
	@echo

.PHONY: setup
setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	@echo "Virtual environment setup complete. See 'make help' for more options."

.PHONY: run
run:
	$(RUN_CMD)

.PHONY: clean
clean:
	deactivate || true
	rm -rf .venv
	@echo "Cleaned up the virtual environment."

.PHONY: test
test:
	. .venv/bin/activate && python3 -m unittest discover -v -s test/
