from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from main import build_runtime
from src.ui.bridge import run_query_sync
from src.ui.trace_viz import build_trace_graph


EXECUTOR = ThreadPoolExecutor(max_workers=2)


def render_graph(graph):
    st.subheader("Routing Graph")
    st.write("Nodes:", graph["nodes"])
    st.write("Edges:", graph["edges"])
    st.write("Transitions:", graph["transitions"])


def _run_pipeline(goal: str, mode: str):
    runtime = build_runtime(mode=mode)
    timeout_s = 25.0 if mode == "live" else 6.0
    result = run_query_sync(goal, manager=runtime["manager"], timeout_s=timeout_s)
    graph = build_trace_graph(result["transitions"], result["envelopes"])
    return {"result": result, "graph": graph}


def _ensure_state():
    if "job_future" not in st.session_state:
        st.session_state.job_future = None
    if "job_error" not in st.session_state:
        st.session_state.job_error = None


def app():
    _ensure_state()
    st.markdown("E2E_READY")
    st.title("Multi-Agent System Dashboard")

    with st.form("pipeline_form", clear_on_submit=False):
        goal = st.text_input("Business goal", "", key="goal_input")
        mode = st.selectbox("Mode", ["mock", "live"], index=0, key="mode_input")
        submitted = st.form_submit_button("Run")

    if submitted:
        st.write("RUN_TRIGGERED")
        st.session_state.job_error = None
        st.session_state.job_future = EXECUTOR.submit(_run_pipeline, goal, mode)

    future = st.session_state.job_future
    if future is not None and not future.done():
        st.write("PIPELINE_RUNNING")
        st.info("Pipeline running...")
        st.rerun()

    if future is not None and future.done():
        try:
            payload = future.result()
            st.write("PIPELINE_OK")
            st.subheader("Final Output")
            st.json(payload["result"]["output"])
            render_graph(payload["graph"])
        except Exception as exc:
            st.session_state.job_error = str(exc)
            st.write("PIPELINE_ERR")
            st.error(f"Pipeline failed: {exc}")


app()
