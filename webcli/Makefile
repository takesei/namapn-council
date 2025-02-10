version = "0.0.4"
project = "velvety-outcome-448307-f0"
port = 8080

.PHONY: dev-server lint

lint:
	@uvx ruff check --fix
	@uvx ruff format

run-dev-server:
	@uv run streamlit run app.py

build:
	docker build --platform linux/amd64 --tag namaph-council:$(version) .

run-server:
	docker run --platform linux/amd64 -i -t --rm --env PORT=$(port) -p $(port):$(port) namaph-council:$(version)

deploy:
	docker tag namaph-council:$(version) us-west1-docker.pkg.dev/velvety-outcome-448307-f0/namaph-council-streamlit/namaph-council:$(version)
	docker push us-west1-docker.pkg.dev/velvety-outcome-448307-f0/namaph-council-streamlit/namaph-council:$(version)
	gcloud run deploy namaph-council\
		--image   us-west1-docker.pkg.dev/velvety-outcome-448307-f0/namaph-council-streamlit/namaph-council:$(version) \
		--region us-west1 \
		--platform managed \
		--project $(project) \
		--allow-unauthenticated \
		--port $(port)
