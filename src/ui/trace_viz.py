def build_trace_graph(transitions, envelopes):
    if not isinstance(transitions, list) or not transitions:
        raise ValueError("transitions required")

    for env in envelopes:
        if "trace_id" not in env or "kind" not in env:
            raise ValueError("envelope missing required keys")

    nodes = [
        "Orchestrator",
        "Researcher",
        "MessageBus",
        "Writer",
        "Final Output",
    ]
    edges = [
        ("Orchestrator", "Researcher"),
        ("Researcher", "MessageBus"),
        ("MessageBus", "Writer"),
        ("Writer", "Final Output"),
    ]

    return {"nodes": nodes, "edges": edges, "transitions": transitions}
