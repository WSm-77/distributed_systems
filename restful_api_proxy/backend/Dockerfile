FROM python:3.12-slim AS base
WORKDIR /app

COPY ./pyproject.toml ./uv.lock ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:${PATH}"

FROM base AS env_builder
RUN uv sync --frozen --no-dev

FROM base AS builder
COPY --from=env_builder /app/.venv /app/.venv
COPY ./ ./
RUN uv run python -c \
    'from data_models.api_user import ApiUser; \
     from db.db import init_db; \
     init_db()'

FROM base AS runtime
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/ ./

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "server:server", "--reload", "--port", "8000"]
