.PHONY: dev test lint fmt docs docs-serve build install link unlink

dev:
	poetry install

lint:
	poetry run ruff check devkit
	poetry run ruff format --check devkit

fmt:
	poetry run ruff format devkit

test:
	@echo "No automated tests. Use the CLI manually (see docs)."

docs:
	poetry run python scripts/generate_reference.py > docs/commands.md

docs-serve:
	@echo "Docs are Markdown-only under docs/. Nothing to serve."

build:
	poetry build

install:
	pipx install .

link:
	mkdir -p ~/.local/bin
	install -m 0755 bin/devkit ~/.local/bin/devkit
	@echo "Installed: ~/.local/bin/devkit (ensure ~/.local/bin is in PATH)"

unlink:
	rm -f ~/.local/bin/devkit
