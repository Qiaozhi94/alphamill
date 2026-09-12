import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

try:  # Package import is used by the host service; fallback keeps the legacy CLI usable.
    from .db_adapter import healthcheck, latest_ohlcv
    from .generator import generate_placeholder_signal
    from .kronos_real import real_signal
except ImportError:  # pragma: no cover - direct script compatibility only.
    from db_adapter import healthcheck, latest_ohlcv
    from generator import generate_placeholder_signal
    from kronos_real import real_signal


class PredictResponse(BaseModel):
    exchange: str
    symbol: str
    source: str
    model: str
    rows_used: int
    latest_candle: datetime | None
    signal_type: str
    confidence: float
    expected_return: float
    volatility: float
    direction_prob: float
    reason: str


class BatchPredictRequest(BaseModel):
    exchange: str = "binance"
    symbols: list[str]
    limit: int = 120


class BatchPredictResponse(BaseModel):
    exchange: str
    source: str
    model: str
    count: int
    predictions: list[PredictResponse]
    errors: dict[str, str]


app = FastAPI(title="Kronos Signal Service", version="0.1.0")


@app.get("/health")
def health():
    db = healthcheck()
    model_status = real_signal.status()
    service_status = "degraded" if model_status.enabled and not model_status.available else "ok"
    return {
        "status": service_status,
        "service": "kronos-signal",
        "model_loaded": model_status.loaded,
        "model_enabled": model_status.enabled,
        "model_available": model_status.available,
        "model": model_status.model,
        "tokenizer": model_status.tokenizer,
        "device": model_status.device,
        "model_error": model_status.error,
        "database": db,
    }


@app.get("/ohlcv/{symbol:path}")
def ohlcv(symbol: str, exchange: str = "binance", limit: int = Query(default=120, ge=1, le=1000)):
    rows = latest_ohlcv(symbol=symbol, exchange=exchange, limit=limit)
    return {
        "exchange": exchange,
        "symbol": symbol,
        "rows": rows,
        "count": len(rows),
    }


@app.get("/predict/{symbol:path}", response_model=PredictResponse)
def predict(symbol: str, exchange: str = "binance", limit: int = Query(default=120, ge=30, le=1000)):
    return build_prediction(symbol=symbol, exchange=exchange, limit=limit)


@app.post("/predict_batch", response_model=BatchPredictResponse)
def predict_batch(request: BatchPredictRequest):
    if not request.symbols:
        raise HTTPException(status_code=400, detail="symbols must not be empty")
    if request.limit < 30 or request.limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 30 and 1000")

    predictions: list[PredictResponse] = []
    errors: dict[str, str] = {}
    for symbol in request.symbols:
        try:
            predictions.append(
                build_prediction(symbol=symbol, exchange=request.exchange, limit=request.limit)
            )
        except HTTPException as exc:
            errors[symbol] = str(exc.detail)
        except Exception as exc:
            errors[symbol] = str(exc)

    return BatchPredictResponse(
        exchange=request.exchange,
        source=prediction_source(),
        model=prediction_model(),
        count=len(predictions),
        predictions=predictions,
        errors=errors,
    )


def build_prediction(symbol: str, exchange: str, limit: int) -> PredictResponse:
    rows = latest_ohlcv(symbol=symbol, exchange=exchange, limit=limit)
    if not rows:
        raise HTTPException(status_code=404, detail=f"No OHLCV rows found for {exchange} {symbol}")

    source = prediction_source()
    model = prediction_model()
    if real_signal.enabled:
        signal = real_signal.generate_signal(rows)
        source = "kronos"
        model = real_signal.model_path
    else:
        signal = generate_placeholder_signal(rows)

    latest = rows[-1]["time"] if rows else None
    return PredictResponse(
        exchange=exchange,
        symbol=symbol,
        source=source,
        model=model,
        rows_used=len(rows),
        latest_candle=latest,
        **signal,
    )


def prediction_source() -> str:
    return "kronos" if real_signal.enabled else "placeholder"


def prediction_model() -> str:
    return (
        real_signal.model_path if real_signal.enabled else os.getenv("KRONOS_MODEL", "placeholder")
    )
