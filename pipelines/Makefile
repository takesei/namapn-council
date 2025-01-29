pj_id = "velvety-outcome-448307-f0"

deploy-bq-query:
	uv pip compile ./execute_bq_query/pyproject.toml -o ./execute_bq_query/requirements.txt
	gcloud functions deploy execute_bq_query \
		--project ${pj_id} \
		--gen2 \
		--region us-west1 \
		--source ./execute_bq_query \
		--runtime python312 \
		--trigger-http \
		--allow-unauthenticated

deploy-load-master:
	uv pip compile ./load_masterdata/pyproject.toml -o ./load_masterdata/requirements.txt
	gcloud functions deploy load_masterdata \
		--project ${pj_id} \
		--gen2 \
		--region us-west1 \
		--source ./load_masterdata \
		--runtime python312 \
		--trigger-http \
		--allow-unauthenticated

deploy-get-spread-sheet-urls:
	npm --prefix ./get_spread_sheet_urls install ./get_spread_sheet_urls
	npm --prefix ./get_spread_sheet_urls run build
	gcloud functions deploy get_spread_sheet_urls \
		--project ${pj_id} \
		--gen2 \
		--region us-west1 \
		--source ./get_spread_sheet_urls/dist \
		--runtime nodejs22 \
		--trigger-http \
		--entry-point=getSpreadSheetUrls \
		--allow-unauthenticated

get-schema:
	bq --project_id velvety-outcome-448307-f0 ls master_data \
		| sed -e "1d;2d" \
		| sed -e "s/TABLE//"  \
		| xargs -I@ -t bq --project_id velvety-outcome-448307-f0  show --format json  master_data.@ \
		> schema.txt
