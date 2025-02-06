.PHONY: clean

run:
	uv run dbt run

clean:
	uv run dbt clean

test:
	uv run dbt test

seed:
	uv run dbt seed

report:
	uv run edr report --profiles-dir .

elementary:
	uv run dbt deps
	uv run dbt run --select elementary
	@echo "copy profile infos below in profiles.yml"
	dbt run-operation elementary.generate_elementary_cli_profile
