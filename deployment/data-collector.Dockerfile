FROM freqtradeorg/freqtrade:stable

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENTRYPOINT []
CMD ["python", "-m", "alphamill.data_bridge.collector.ccxt_ingestor"]
