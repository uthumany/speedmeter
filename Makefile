# =============================================================================
# SpeedMeter — Makefile
# =============================================================================
# Common development tasks for the SpeedMeter project.
# Usage: make <target>
# =============================================================================

.PHONY: install install-dev test test-verbose lint format build clean all

# Install the package in editable mode (production dependencies only)
install:
	pip install -e .

# Install the package with dev dependencies (testing, linting, etc.)
install-dev:
	pip install -e ".[dev]"

# Run test suite (fast mode)
test:
	pytest

# Run test suite with verbose output
test-verbose:
	pytest -v

# Lint the codebase with ruff
lint:
	ruff check

# Auto-format the codebase with ruff
format:
	ruff format

# Build a standalone executable with PyInstaller
# Uses speedmeter/widget.spec if it exists
build:
	if [ -f speedmeter/widget.spec ]; then \
		pyinstaller speedmeter/widget.spec; \
	else \
		echo "No widget.spec found. Run 'make widget-spec' first or create speedmeter/widget.spec"; \
		exit 1; \
	fi

# Clean up build artifacts, caches, and temporary files
clean:
	rm -rf __pycache__ .pytest_cache build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true

# Run full pipeline: lint → test → build
all: lint test build
