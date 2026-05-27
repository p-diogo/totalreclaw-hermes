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

On bootstrap, the plugin auto-installs the canonical TotalReclaw SKILL.md
into `~/.hermes/skills/memory/totalreclaw/SKILL.md` so the Hermes skill
loader picks it up. Hermes loads SKILL.md files via `rglob` over
`<HERMES_HOME>/skills/**/SKILL.md` on every turn — without the file at
that path, the agent has no behavioural guidance on when to prefer
TotalReclaw tools over Hermes' built-in `memory`.

**Source of truth: the installed `totalreclaw` Python package.** The
SKILL.md ships in the PyPI wheel as `package_data` (see
`[tool.setuptools.package-data]` in `pyproject.toml`). On every plugin
bootstrap, `__init__.py` reads it via
`importlib.resources.files("totalreclaw.hermes").joinpath("SKILL.md")`
and writes it to the skills dir. Idempotent — skip if destination
content already matches; overwrite on upgrade if it differs.

Why route through the Python package and not ship a SKILL.md in this
Git repo: prior to 2026-05-28 the canonical SKILL.md lived in this
repo, drifted from the Python package's version across 5 RC cycles
(tier copy, recall behaviour, restart-branch table, phrase-safety
hardening), and Hermes-the-agent improvised stub versions when its
context dropped the original. Single source of truth fixes that.

Legacy location `~/.hermes/skills/devops/totalreclaw-memory/` (the
agent's improvised destination on a 2026-05-26 commit) is `rm -rf`'d
on bootstrap if present.

Behavioural guidance the agent gets from the skill includes:

- When to use `totalreclaw_remember` vs the built-in `memory` tool
  (always prefer TotalReclaw for durable user facts, preferences, decisions)
- When to use `totalreclaw_recall` (per the rc.5 recall rule — call it
  on every recall query the user issues, even when context appears to
  hold the answer)
- Tier + pricing canon (2.4.1+): 250 / 1,500 caps on Gnosis mainnet,
  no "unlimited" claim, no "free trial" claim
- Restart-branch matrix by surface (Telegram / docker CLI / native CLI / ask)
- Phrase safety: never ask user to paste recovery phrase in chat; if
  they do, treat as compromised and re-pair

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
