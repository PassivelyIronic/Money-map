FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# najpierw same zaleznosci, zeby docker cache'owal ta warstwe
# dopoki pyproject.toml/uv.lock sie nie zmienia
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# potem kod aplikacji
COPY app ./app
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
