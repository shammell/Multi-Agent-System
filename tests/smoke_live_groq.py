import os

from main import build_runtime
from src.ui.bridge import run_query_sync


def main():
    runtime = build_runtime(mode="live")
    result = run_query_sync(
        "Summarize current solar market opportunities in Karachi in 3 bullets.",
        manager=runtime["manager"],
        timeout_s=float(os.getenv("GROQ_TIMEOUT_SECONDS", "25")),
        trace_id="live-smoke",
    )

    assert result["output"]["kind"] == "DraftPayload"
    print("LIVE_SMOKE_OK", result["output"]["payload"]["draft"][:200])


if __name__ == "__main__":
    main()
