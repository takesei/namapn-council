FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen

ENV PATH=/root/.local/bin:$PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=7777

EXPOSE $PORT
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health
CMD ["/bin/bash", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"]
