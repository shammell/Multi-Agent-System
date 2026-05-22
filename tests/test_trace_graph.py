from src.ui.trace_viz import build_trace_graph


def test_build_trace_graph_happy_path():
    envelopes = [
        {"trace_id": "t1", "kind": "TaskEnvelope"},
        {"trace_id": "t1", "kind": "ResearchPayload"},
        {"trace_id": "t1", "kind": "DraftPayload"},
    ]
    transitions = ["RECEIVED", "RESEARCHED", "DRAFTED", "COMPLETED"]

    graph = build_trace_graph(transitions, envelopes)

    assert "nodes" in graph and "edges" in graph
    assert len(graph["nodes"]) >= 5
    assert len(graph["edges"]) >= 4


def test_build_trace_graph_rejects_missing_trace_id():
    envelopes = [{"kind": "TaskEnvelope"}]
    transitions = ["RECEIVED"]
    try:
        build_trace_graph(transitions, envelopes)
        assert False, "expected ValueError"
    except ValueError:
        assert True
