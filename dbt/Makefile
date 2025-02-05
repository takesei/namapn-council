.PHONY: clean

run:
	uv run dbt run

clean:
	uv run dbt clean

report:
	uv run edr report --profiles-dir .

elementary:
	uv run dbt deps
	uv run dbt run --select elementary
	dbt run-operation elementary.generate_elementary_cli_profile
