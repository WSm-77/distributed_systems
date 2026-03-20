FROM python:3.12 AS runtime
WORKDIR /app

COPY . .

RUN apt update && apt install -y curl

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

RUN uv sync

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "server:server", "--reload", "--port", "8000"]
