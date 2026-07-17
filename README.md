# heard

> Voice-controlled tooling daemon for Linux. Speech to intent resolution to tool dispatch. Local-first.

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white&style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-10AC84?style=for-the-badge)]()
[![Arch](https://img.shields.io/badge/Target-Arch%20Linux-1793D1?logo=archlinux&logoColor=white&style=for-the-badge)]()

hear + d. It's the joke `sshd` would make if it could. Reads as an English word, is exactly what the daemon does, and `heard: launching spotify` in a log line is funny. 

> **WIP.** v0.1 is a foreground blocking loop that is **still being built**. This readme represents the v0.1 final state. Kill with Ctrl-C. Daemonization arrives in v1.
---

## Quick start

```bash
uv run -m heard.cli listen
```

Push-to-talk, say a command, watch it execute. That is the v0.1 loop:

1. Capture audio (keybind press or silence detection)
2. Transcribe via local Whisper (runs entirely on-device)
3. Resolve intent via Needle (a 26M parameter function-call model)
4. Dispatch to the matching tool handler (launch, media, volume, window, workspace, system query)
5. Print result to stdout

6 tools, all local, no network, no daemonization. The entire pipeline stays under ~2s from speech end to action.

---

## Why Needle?

heard routes spoken commands to tool calls. That is a classification problem, not a general reasoning problem. A 26M function-call model like Needle is the right tool for three reasons:

**Speed.** A larger LLM adds seconds of latency on consumer hardware. Needle loads in tens of milliseconds and generates a tool-call in under 200ms on a modern CPU. That keeps the end-to-end pipeline fast enough for voice interactions (speech in, action out, no perceptible delay).

**Local-first.** Larger models often require cloud APIs or high-end GPUs. Needle runs on a laptop CPU with no special hardware and no network round trip. The only feature that ever touches the network is the optional `answer_query` fallback (v1), which is explicitly opt-in.

**Specialization.** A 7B+ general-purpose model dedicates most of its capacity to knowledge and dialogue. Needle is trained specifically for function-call extraction from natural language. Tool descriptions are the primary steering signal; tightening them alone moved accuracy from 75% to 92% in probing with no additional training data. A smaller, narrower model is harder to get wrong and easier to finetune.

The tradeoff: Needle is not a chat model. It does not answer questions, hold context, or handle multi-turn dialogue. That is intentional. Every tool call is stateless and single-shot. When the user asks something open-ended ("what is the weather tomorrow?"), Needle only decides _that_ the input needs a text answer; the actual answering is delegated to a full LLM (v1). This keeps Needle's job narrow and reliable.

---

## Tools (v0.1)

| Tool | Handler | What it does |
|---|---|---|
| `launch_app` | `tools/apps.py` | Launch an application by binary name |
| `media_control` | `tools/media.py` | Play, pause, next, previous track (MPRIS over D-Bus) |
| `volume_control` | `tools/volume.py` | Up, down, mute, set percent (PipeWire via wpctl) |
| `window_action` | `tools/window.py` | Close, focus, fullscreen a window (hyprctl) |
| `workspace_switch` | `tools/workspace.py` | Switch workspace by number (hyprctl) |
| `system_query` | `tools/system_query.py` | Battery, time, network, disk status |

Tool schemas are generated from the registry (not stored as a static file), so descriptions, validation enums, and finetune data all derive from one source. No drift between what the model sees and what dispatch accepts.

---

## Architecture (v0.1)

```
capture audio -> stt.py (Whisper) -> intent.py (Needle) -> tools/registry.py -> handler
                                                                                      |
                                                                               stdout result
```

Every component is a single file under `heard/`. No persistence, no analytics, no responder process. The intent model loads once as a lazy module-level singleton and stays hot for the lifetime of the process.

The dispatcher (`tools/registry.py`) holds a `dict[str, Callable]` mapping tool names to handler functions. It never passes raw model output to a shell. Arguments are matched against the tool schema and dispatched with `handler(**arguments)`. The `shell_allowlist.py` provides known-safe command templates for the few tools that need subprocess execution; the model selects an allowlisted action, never arbitrary shell text.

---

## Repo structure

```
heard/
├── pyproject.toml
├── heard/
│   ├── cli.py                 # entrypoint: heard listen
│   ├── stt.py                 # whisper capture + transcription
│   ├── intent.py              # Needle load + generate wrapper
│   ├── shell_allowlist.py     # safe command templates
│   └── tools/
│       ├── registry.py        # name -> handler dispatch
│       ├── apps.py            # launch_app
│       ├── media.py           # media_control
│       ├── volume.py          # volume_control
│       ├── window.py          # window_action (hyprctl)
│       ├── workspace.py       # workspace_switch (hyprctl)
│       ├── system_query.py    # battery, time, network, disk
│       └── helpers/
│           ├── network.py     # connectivity checks
│           └── system.py      # format_bytes etc.
├── checkpoints/               # gitignored, needle weights
└── data/
    └── tools.json             # tool schema definitions
```

---

## Acceptance criteria (v0.1)

- Each of the 6 tools resolves correctly from casual phrasing at least 5/6 times.
- End-to-end latency from speech end to action executed stays under ~2s on local hardware.
- Unresolvable input prints "didn't understand" to stdout; it never crashes.

---

## Roadmap (v1)

v0.1 proves the capture-resolve-dispatch path. v1 adds the infrastructure for a production voice assistant: daemonization, feedback loops, analytics, and multi-desktop support.

| Area | What lands |
|---|---|
| **Daemon** | Persistent background process with systemd user unit; optional wake-word support alongside push-to-talk |
| **Responder** | Floating GTK popup and local TTS (piper/espeak-ng); runs as a separate process over a unix socket so the daemon stays non-blocking |
| **Confidence gating** | `answer_query` escape hatch for low-confidence or open-ended input, forwarded to an LLM API (Claude/ChatGPT) for the actual response |
| **Analytics** | ClickHouse event logging with latency breakdown (STT vs intent); Prefect daily rollups and a retrain pipeline that converts failures into finetune data |
| **WM backends** | Sway and KDE support alongside the v0.1 Hyprland backend; backend detection with explicit config override for the systemd environment gap |
| **API** | FastAPI stats surface: `/events`, `/stats/daily`, `/health` |

The model stays 26M Needle at the core. v1 adds the confidence thresholds, fallback paths, observability, and persistent process lifecycle around it.
