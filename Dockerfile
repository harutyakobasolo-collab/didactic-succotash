FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY mock_service ./mock_service
COPY examples ./examples

RUN python -m pip install --no-cache-dir ".[mock]"

CMD ["uvicorn", "mock_service.app:app", "--host", "0.0.0.0", "--port", "8000"]

