"""Kronos health truthfulness regression tests."""

from alphamill.kronos_service import server
from alphamill.kronos_service.kronos_real import ModelStatus


def test_health_reports_degraded_when_enabled_model_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(server, "healthcheck", lambda: {"total_rows": 1})
    monkeypatch.setattr(
        server.real_signal,
        "status",
        lambda: ModelStatus(
            enabled=True,
            available=False,
            loaded=False,
            model="models/Kronos-base",
            tokenizer="models/Kronos-Tokenizer-base",
            device="cpu",
            error="missing torch",
        ),
    )

    payload = server.health()

    assert payload["status"] == "degraded"
    assert payload["model_enabled"] is True
    assert payload["model_available"] is False
