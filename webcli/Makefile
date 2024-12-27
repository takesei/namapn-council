.PHONY: dev-server lint

lint:
	@uvx ruff check

run-dev-server:
	@uv run streamlit run app.py

migration:
	@uv run python ./TEMP/migration.py
