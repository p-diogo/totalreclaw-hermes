# TotalReclaw Hermes Plugin

End-to-end encrypted memory for your Hermes agent. Persistent across sessions,
portable across agents, stored on-chain (Base / Gnosis). Your phrase never
crosses the LLM context.

## Install

```bash
hermes plugins install p-diogo/totalreclaw-hermes
```

## Post-install

The Git plugin is a thin wrapper that delegates to the `totalreclaw` Python
package. Install it inside the same environment Hermes runs from:

```bash
pip install --pre totalreclaw
hermes gateway restart
```

If `totalreclaw` is already installed in your Hermes venv, only the restart
is needed.

## Setup

Paste this into your chat:

```
Set up TotalReclaw
```

The agent drives a QR-pair flow: it gives you a URL and a 6-digit PIN. Open
the URL in your browser, enter the PIN, and either generate a new 12-word
recovery phrase or paste your existing one. The phrase is encrypted
browser-side and uploaded end-to-end encrypted to the gateway — it never
touches the LLM or this chat transcript.

Once pairing completes, restart the gateway so the plugin picks up the new
credentials, then try:

```
remember I prefer short meetings
recall what you know about my meeting preferences
```

## What's in this plugin

- `totalreclaw_remember` — store an encrypted memory (claims, preferences, directives, commitments, episodes, summaries)
- `totalreclaw_recall` — BM25 + semantic search with Tier 1 source-weighted reranking
- `totalreclaw_pair` — browser-side recovery-phrase setup (phrase-safe)
- `totalreclaw_pin` / `totalreclaw_unpin` — protect a canonical memory from automatic supersession
- `totalreclaw_status` — billing / usage / tier info
- `totalreclaw_upgrade` — TotalReclaw Pro Stripe checkout flow
- `totalreclaw_import_from` / `totalreclaw_import_batch` — migrate memories from Gemini, ChatGPT, Claude, Mem0, mcp-memory, generic JSON
- `totalreclaw_forget` / `totalreclaw_export` / `totalreclaw_debrief`

RC builds additionally expose `totalreclaw_report_qa_bug` (hidden in stable).

## Why a separate Git plugin?

Hermes 2026.4.16+ discovers plugins via Git clone into
`~/.hermes/plugins/<name>/` plus a `plugin.yaml` + `__init__.py` at the
repo root. It does not consult the Python entry-points that the
`totalreclaw` PyPI package ships with. This repo provides that thin
Hermes-native surface; all the logic stays in the maintained
`totalreclaw` package.

## Links

- Main repo: <https://github.com/p-diogo/totalreclaw>
- Setup guide: <https://github.com/p-diogo/totalreclaw/blob/main/docs/guides/hermes-setup.md>
- PyPI package: <https://pypi.org/project/totalreclaw/>
- Issues: <https://github.com/p-diogo/totalreclaw/issues>

## License

MIT
