from main import build_runtime


def test_build_runtime_mock_mode():
    runtime = build_runtime(mode="mock")
    assert "bus" in runtime
    assert "manager" in runtime
    assert "researcher" in runtime
    assert "writer" in runtime
