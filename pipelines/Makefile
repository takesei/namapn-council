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

deploy-save-master-to-drive:
	uv pip compile ./save_masterdata_to_drive/pyproject.toml -o ./save_masterdata_to_drive/requirements.txt
	gcloud functions deploy save_masterdata_to_drive \
		--project ${pj_id} \
		--gen2 \
		--region us-west1 \
		--source ./save_masterdata_to_drive \
		--runtime python312 \
		--trigger-http \
		--allow-unauthenticated

deploy-update-spread-sheet:
	gcloud functions deploy update_spread_sheet \
		--project ${pj_id} \
		--gen2 \
		--region us-west1 \
		--source ./update_spread_sheet \
		--runtime nodejs22 \
		--trigger-http \
		--entry-point=updateSpreadSheet \
		--allow-unauthenticated

dataset = "mart"
get-schema:
	bq --project_id velvety-outcome-448307-f0 ls ${dataset} \
		| sed -e "1d;2d" \
		| sed -e "s/TABLE//"  \
		| xargs -I@ -t bq --project_id velvety-outcome-448307-f0  show --format json  ${dataset}.@ \
		> schema.txt
