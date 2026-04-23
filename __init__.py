"""Hermes Git plugin for TotalReclaw — rc.10 auto-bootstrap edition.

Installable via ``hermes plugins install p-diogo/totalreclaw-hermes``.

The heavy lifting — tool handlers, pair-server crypto, HTTP pairing
server, agent hooks — lives in the ``totalreclaw`` Python package on
PyPI. This Git plugin is a thin wrapper that makes TotalReclaw
discoverable to Hermes via its Git-plugin system (``plugin.yaml`` +
``__init__.py`` at repo root).

rc.10 self-heals three friction points observed on Docker Hermes:

1. ``pip install totalreclaw`` landing in user-site when Hermes venv has
   ``ENABLE_USER_SITE=False`` (import fails silently despite pip success).
2. Hermes venv missing pip entirely (e.g. ``uv venv``, ``virtualenv --without-pip``).
3. ``~/.totalreclaw/`` owned by root under a Docker volume mount while
   Hermes runs as a non-root uid, so the first lock-file create fails.

All bootstrap paths raise ``RuntimeError`` with actionable guidance rather
than failing silently. Each step is idempotent — re-running the bootstrap
on a healthy install is a no-op.

See:
- https://github.com/p-diogo/totalreclaw
- https://github.com/p-diogo/totalreclaw/blob/main/docs/guides/hermes-setup.md
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _ensure_pip_in_venv() -> None:
    """If running inside a venv that lacks pip (common on ``uv venv`` or
    ``virtualenv --without-pip``), bootstrap pip via ensurepip before any
    install attempt."""
    try:
        import pip  # noqa: F401
        return
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Hermes venv lacks pip AND ensurepip failed. "
            "Run `python -m ensurepip` manually inside your venv, "
            "then restart the Hermes gateway."
        ) from exc


def _install_totalreclaw_in_venv() -> None:
    """Ensure the ``totalreclaw`` Python package is importable by the
    CURRENT Python interpreter. If a prior ``pip install`` landed in
    user-site (because the Hermes venv has ``ENABLE_USER_SITE=False``)
    or never ran at all, install it now using the venv's own pip so it
    lands in venv site-packages."""
    try:
        import totalreclaw  # noqa: F401
        return
    except ImportError:
        pass
    _ensure_pip_in_venv()
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--pre",
            "--no-cache-dir",
            "--index-url",
            "https://pypi.org/simple/",
            "--no-warn-script-location",
            "totalreclaw",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _ensure_state_dir_writable() -> None:
    """Ensure ``~/.totalreclaw`` is writable by the current process user.

    On Docker with volume mounts the directory is sometimes created owned
    by root (because the container's first writer was root) while Hermes
    runs as a non-root uid. This raises ``PermissionError`` on the first
    ``pair-sessions.json.lock`` create, long after the plugin loads.

    We surface it at plugin load with a message that tells the user
    exactly what to chown."""
    state = Path.home() / ".totalreclaw"
    try:
        state.mkdir(mode=0o755, exist_ok=True)
    except PermissionError as exc:
        raise RuntimeError(
            f"~/.totalreclaw ({state}) is not writable by the current "
            f"process user (uid={os.geteuid()}). Fix: from the HOST run "
            f"`docker exec <hermes-container> chown -R $(id -u):$(id -g) {state}`, "
            f"OR recreate the volume mount owned by the container uid."
        ) from exc

    probe = state / ".write-probe"
    try:
        probe.write_text("ok")
        probe.unlink()
    except (PermissionError, OSError) as exc:
        raise RuntimeError(
            f"~/.totalreclaw exists ({state}) but the current process "
            f"cannot write. uid={os.geteuid()}; inspect with `ls -la {state}`. "
            f"Chown the directory to the Hermes runtime user."
        ) from exc


def _bootstrap() -> None:
    _install_totalreclaw_in_venv()
    _ensure_state_dir_writable()


_bootstrap()

# After bootstrap, the real register() is importable.
from totalreclaw.hermes import register as _register  # noqa: E402


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
