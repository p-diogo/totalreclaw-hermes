"""Hermes Git plugin for TotalReclaw.

Installable via ``hermes plugins install p-diogo/totalreclaw-hermes``.

The heavy lifting — tool handlers, pair-server crypto, HTTP pairing
server, agent hooks — lives in the ``totalreclaw`` Python package on
PyPI. This Git plugin is a thin wrapper that makes TotalReclaw
discoverable to Hermes via its Git-plugin system (``plugin.yaml`` +
``__init__.py`` at repo root).

Hermes (2026.4.16+) discovers plugins by cloning a Git repo into
``~/.hermes/plugins/<name>/`` and calling ``register(ctx)`` on the
module defined here. The prior Python-entry-point discovery mechanism
that the upstream ``totalreclaw`` package uses is not consulted by
current Hermes builds, so this wrapper is required.

See:
- https://github.com/p-diogo/totalreclaw
- https://github.com/p-diogo/totalreclaw/blob/main/docs/guides/hermes-setup.md
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from totalreclaw.hermes import register as _register
except ImportError as exc:  # pragma: no cover — surfaced to user
    raise RuntimeError(
        "totalreclaw Python package not installed. Run "
        "`pip install --pre totalreclaw` inside your Hermes venv, then "
        "`hermes gateway restart`. See "
        "https://github.com/p-diogo/totalreclaw-hermes#post-install for "
        "details."
    ) from exc


def register(ctx):
    """Hermes calls this on plugin load.

    Delegates to ``totalreclaw.hermes.register`` which wires all
    ``totalreclaw_*`` tools (remember, recall, pair, pin, unpin, status,
    upgrade, debrief, import_from, import_batch, forget, export) plus
    the four agent-lifecycle hooks (on_session_start, pre_llm_call,
    post_llm_call, on_session_end) into the provided ``ctx``.

    The RC-gated ``totalreclaw_report_qa_bug`` tool is registered too
    when the installed ``totalreclaw`` wheel is a pre-release (PEP-440
    ``rcN`` or SemVer ``-rc.N``) build.
    """
    logger.info("totalreclaw Git plugin loading — delegating to totalreclaw.hermes.register")
    return _register(ctx)
