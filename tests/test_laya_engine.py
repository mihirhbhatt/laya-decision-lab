import laya

from laya_labs.engine.laya_engine import LayaEngine


def test_laya_engine_uses_router_for_default_model_selection(monkeypatch):
    calls = []

    class FakeRouter:
        def __init__(self, device=None):
            calls.append(("router", device))

        def predict(self, state, questions):
            return {"answers": {}}

    monkeypatch.setattr(laya, "Router", FakeRouter)
    engine = LayaEngine(device="cpu")

    result = engine.predict("hello", {})

    assert calls == [("router", "cpu")]
    assert result == {"answers": {}}


def test_laya_engine_preserves_explicit_checkpoint_loading(monkeypatch):
    calls = []
    fake_agent = object()

    def fake_load(model, device=None):
        calls.append((model, device))
        return fake_agent

    monkeypatch.setattr(laya, "load", fake_load)
    engine = LayaEngine(model="local-checkpoint", device="cpu")

    assert engine.load() is fake_agent
    assert calls == [("local-checkpoint", "cpu")]