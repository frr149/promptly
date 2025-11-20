.PHONY: help install test lint clean examples

help:
	@echo "Comandos disponibles:"
	@echo "  make install   - Instalar paquete en modo editable con dependencias de dev"
	@echo "  make test      - Ejecutar tests con coverage"
	@echo "  make lint      - Ejecutar linter (ruff)"
	@echo "  make clean     - Limpiar archivos temporales y cache"
	@echo "  make examples  - Ejecutar ejemplos de uso"

install:
	uv pip install -e ".[dev]"

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/ examples/

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

examples:
	@echo "=== Running basic examples ==="
	uv run python examples/basic_usage.py
	@echo ""
	@echo "=== Running advanced examples ==="
	uv run python examples/advanced_usage.py
