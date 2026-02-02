SHELL := /bin/bash

.PHONY: help
help:
	@echo
	@echo "Makefile commands:"
	@echo "  make setup  - Set up the Python virtual environment and install dependencies."
	@echo "  make run    - Run the main Python application. Use cases:"
	@echo "      make run [config-file] [document-file] > [output-file]"
	@echo "           Contextual translation of the document-file."
	@echo "           The config-file is a '.yaml' file that defines the translation settings."
	@echo "           The result is written to the standard output,"
	@echo "           which can be redirected to an output-file."
	@echo
	@echo "      make run --dry-run [config-file] [document-file] > [output-file]"
	@echo "           Executes only the regex replacements defined in the config-file,"
	@echo "           without loading the model."
	@echo
	@echo '      make run --one-shot [target-language-code] "text-segment"'
	@echo "           Translates a single text segment without context and config file."
	@echo "           Outputs the translated text segment to standard output."
	@echo "           Use this for translating the 'static context' for the config file."
	@echo "           The target-language-code is in BCP-47 format (e.g., 'en' for English)."
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
	. .venv/bin/activate && python3 main.py

.PHONY: clean
clean:
	deactivate || true
	rm -rf .venv
	@echo "Cleaned up the virtual environment."

.PHONY: test
test:
	python3 -m unittest discover -v -s test/
