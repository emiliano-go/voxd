import json, time
from dataclasses import dataclass
from functools import lru_cache

from needle import SimpleAttentionNetwork, generate, get_tokenizer, load_checkpoint
from .tools import registry

MAX_GEN_LEN = 64

CHECKPOINT_PATH = "checkpoints/needle_checkpoint.pkl"

@dataclass(frozen=True)
class Resolution:
    raw_query: str
    tool_call: dict | None
    reason: str | None
    latency_ms: float | None


@lru_cache(maxsize=1)
def _model():
    """Load once. ~1s load + ~8s JIT on first generate()"""

    params, config = load_checkpoint(CHECKPOINT_PATH)
    return SimpleAttentionNetwork(config), params, get_tokenizer()

@lru_cache(maxsize=1)
def _tools_json() -> str:
    return json.dumps(registry.known_tools())


def resolve(query: str) -> Resolution:
    model, params, tok = _model()
    t0 = time.perf_counter()
    raw = generate(model, params, tok, query=query,
                   tools=_tools_json(), stream=False, max_gen_len=MAX_GEN_LEN)
    ms = (time.perf_counter() - t0) * 1000

    try:
        calls = json.loads(raw)
    except ValueError:
        return Resolution(query, None, "unparseable", ms)
    if not calls:
        return Resolution(query, None, "declined", ms)    # [] is correct output
    return Resolution(query, calls[0], None, ms)          # single-shot by design

def warmup() -> None:
    resolve("test")