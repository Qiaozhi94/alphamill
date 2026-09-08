FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8001
CMD ["uvicorn", "alphamill.kronos_service.server:app", "--host", "0.0.0.0", "--port", "8001"]
