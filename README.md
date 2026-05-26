# TotalReclaw Hermes Plugin

End-to-end encrypted memory for your Hermes agent. Persistent across sessions,
portable across agents, stored on-chain (Base / Gnosis). Your phrase never
crosses the LLM context.

## Install

```bash
hermes plugins install p-diogo/totalreclaw-hermes
```

## Post-install

rc.10+ self-bootstraps on first `hermes gateway restart`. The plugin installs
the `totalreclaw` Python package into the Hermes venv (bypassing user-site
if `ENABLE_USER_SITE=False`), bootstraps pip via `ensurepip` if the venv was
created `--without-pip`, and verifies `~/.totalreclaw/` is writable by the
Hermes runtime user. No manual `pip install` is required.

```bash
hermes gateway restart
```

Any bootstrap failure surfaces as a `RuntimeError` with actionable guidance
(e.g. if `~/.totalreclaw/` is root-owned under a Docker volume mount, the
error includes the exact `chown` command to run from the host).

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

## Bundled Skill

The plugin ships a `SKILL.md` that is automatically installed into
`~/.hermes/skills/devops/totalreclaw-memory/` on bootstrap. This skill is
loaded into the agent's context on every turn and teaches it:

- **When to use `totalreclaw_remember`** vs the built-in `memory` tool (always
  prefer TotalReclaw for durable user facts, preferences, and decisions)
- **When to use `totalreclaw_recall`** vs built-in memory (fallback for any
  fact not in working memory, and the canonical store for all user data)
- **Cross-platform awareness** — TotalReclaw may hold data from other AI tools
  (ChatGPT, Gemini, OpenClaw) and imported conversation history
- **Phrase safety rules** — never ask the user to paste a recovery phrase in chat

The skill install is idempotent and auto-updates on plugin upgrade.

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
