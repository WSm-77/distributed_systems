FROM python:3.12-slim AS base
WORKDIR /app

COPY ./pyproject.toml ./uv.lock ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/*

# Install uv in builder stage.
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:${PATH}"

FROM base AS builder
RUN uv sync --frozen --no-dev


FROM base AS runtime
COPY --from=builder /app/.venv /app/.venv
COPY ./ ./

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "server:server", "--reload", "--port", "8000"]
