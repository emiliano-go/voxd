"""Bare-metal latency probe for Needle on heard.

Usage: uv run python scripts/benchmark_latency.py
"""

import json
import statistics
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from needle import generate, get_tokenizer, load_checkpoint, SimpleAttentionNetwork
from heard.tools.registry import known_tools

CHECKPOINT = "checkpoints/needle_checkpoint.pkl"
MAX_GEN_LEN = 64

PROBES = [
    # system_query
    "What time is it?",
    "How's my battery?",
    "Check the network status",
    "How much disk space is left?",
    # volume_control
    "Turn the volume up",
    "Turn it down a bit",
    "Mute the audio",
    "Set the volume to 50 percent",
    # media_control
    "Play some music",
    "Pause the playback",
    "Skip to the next track",
    "Go back to the previous song",
    # launch_app
    "Open Firefox",
    "Launch the calculator",
    "Start VS Code",
    # window_action
    "Close this window",
    "Make it fullscreen",
    "Focus on the browser",
    # workspace_switch
    "Go to workspace 1",
    "Switch to workspace 3",
]


def _load():
    print("Loading model ...", end=" ", flush=True)
    t0 = time.perf_counter()
    params, config = load_checkpoint(CHECKPOINT)
    model = SimpleAttentionNetwork(config)
    tok = get_tokenizer()
    elapsed = time.perf_counter() - t0
    print(f"{elapsed*1000:.0f}ms")
    return model, params, tok


def _warmup(model, params, tok, tools_json):
    print("Warmup ...", end=" ", flush=True)
    t0 = time.perf_counter()
    generate(model, params, tok, query="test", tools=tools_json,
             stream=False, max_gen_len=MAX_GEN_LEN)
    elapsed = time.perf_counter() - t0
    print(f"{elapsed*1000:.0f}ms")


def run_constrained(model, params, tok, tools_json, label: str, constrained: bool):
    print(f"\n--- {label} ---")
    latencies = []
    correct_tool = 0
    parseable = 0

    for q in PROBES:
        t0 = time.perf_counter()
        raw = generate(model, params, tok, query=q, tools=tools_json,
                       stream=False, max_gen_len=MAX_GEN_LEN,
                       constrained=constrained)
        ms = (time.perf_counter() - t0) * 1000
        latencies.append(ms)

        try:
            calls = json.loads(raw)
            parseable += 1
            if calls and isinstance(calls, list):
                correct_tool += 1
        except (ValueError, TypeError):
            pass

        print(f"  {ms:8.0f}ms  {q}")

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    avg = statistics.mean(latencies)
    print(f"\n{label} — {len(latencies)} probes")
    print(f"  avg {avg:.0f}ms  p50 {p50:.0f}ms  p95 {p95:.0f}ms  max {max(latencies):.0f}ms")
    print(f"  parseable {parseable}/{len(PROBES)}  tool-call {correct_tool}/{len(PROBES)}")
    return latencies


def main():
    tools_json = json.dumps(known_tools())
    model, params, tok = _load()
    _warmup(model, params, tok, tools_json)

    c_latencies = run_constrained(model, params, tok, tools_json,
                                  "CONSTRAINED", constrained=True)
    u_latencies = run_constrained(model, params, tok, tools_json,
                                  "UNCONSTRAINED", constrained=False)

    print("\n--- COMPARISON ---")
    for label, lat in [("constrained  ", c_latencies), ("unconstrained", u_latencies)]:
        lat.sort()
        print(f"  {label}:  avg {statistics.mean(lat):.0f}ms  "
              f"p50 {statistics.median(lat):.0f}ms  "
              f"p95 {lat[int(len(lat)*0.95)]:.0f}ms  "
              f"max {max(lat):.0f}ms")


if __name__ == "__main__":
    main()
