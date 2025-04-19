FROM ghcr.io/katagaki/lingus:latest
WORKDIR /app

RUN mkdir -p ./web/
COPY pyproject.toml ./web/
COPY uv.lock ./web/
RUN uv pip install ./web

COPY web ./web/
COPY app.py ./web_server.py

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000"]