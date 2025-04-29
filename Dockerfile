FROM python:3.12.2-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.1

COPY pyproject.toml poetry.lock ./
COPY start.sh /app/start.sh

COPY api ./api

RUN poetry install --without dev --no-root

RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
