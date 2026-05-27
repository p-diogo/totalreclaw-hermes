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


def _install_skill() -> None:
    """Copy the authoritative SKILL.md from the installed ``totalreclaw``
    Python package into the Hermes skills directory so it loads into agent
    context on every turn.

    Source-of-truth design (2026-05-28): the SKILL.md lives ONLY in the
    Python package at ``totalreclaw/hermes/SKILL.md`` (shipped via
    ``[tool.setuptools.package-data]`` in the wheel). This plugin repo
    no longer carries its own SKILL.md — that file historically drifted
    from the canonical version (5 RC cycles of tier copy, recall
    behaviour, restart-branch table, phrase-safety hardening all landed
    in the python package but never reached Hermes' skill loader). See
    p-diogo/totalreclaw-internal#335 for full context.

    Destination ``<HERMES_HOME>/skills/memory/totalreclaw/SKILL.md`` —
    the ``memory`` category matches upstream Hermes' bundled memory-
    provider conventions (Honcho/Byterover/OpenViking).

    Cleanup: removes the legacy
    ``<HERMES_HOME>/skills/devops/totalreclaw-memory/`` path if present
    (Hermes-the-agent improvised that location in a 2026-05-26 commit
    on this repo's ``feat/skill-md`` branch before the canonical
    mechanism existed; ``rm -rf`` only that exact subdir).

    Idempotent — skips write if destination content matches source.
    Non-fatal: any OSError is logged + swallowed so plugin load never
    fails on a SKILL.md write hiccup.
    """
    try:
        from importlib.resources import files as _resource_files
    except ImportError:  # pragma: no cover — Python <3.9
        logger.debug("importlib.resources.files unavailable — skipping skill install")
        return

    try:
        src_text = _resource_files("totalreclaw.hermes").joinpath("SKILL.md").read_text(encoding="utf-8")
    except (ModuleNotFoundError, FileNotFoundError, OSError) as exc:
        # `totalreclaw` not installed yet, or its SKILL.md package-data missing.
        # Bootstrap order ensures the wheel is installed before this runs (see
        # _install_totalreclaw_in_venv above) — if we still can't read SKILL.md,
        # log + skip rather than crashing plugin load.
        logger.debug("Could not read totalreclaw.hermes/SKILL.md from package: %s", exc)
        return

    try:
        from hermes_constants import get_hermes_home
    except ImportError:
        logger.debug("hermes_constants not available — skipping skill install")
        return

    hermes_home = get_hermes_home()

    # Cleanup legacy path. The agent-improvised location was
    # ``skills/devops/totalreclaw-memory/``. Remove only that exact subdir
    # if it exists, leave neighbouring skills alone.
    legacy_dir = hermes_home / "skills" / "devops" / "totalreclaw-memory"
    if legacy_dir.exists():
        try:
            import shutil
            shutil.rmtree(legacy_dir)
            logger.info("Removed legacy TotalReclaw skill location %s", legacy_dir)
        except OSError as exc:
            logger.debug("Could not remove legacy skill dir %s: %s", legacy_dir, exc)
        # Don't bail on cleanup failure — proceed to install the new location.

    skills_dir = hermes_home / "skills" / "memory" / "totalreclaw"
    dst = skills_dir / "SKILL.md"

    if dst.exists() and dst.read_text(encoding="utf-8") == src_text:
        return  # already up to date

    try:
        skills_dir.mkdir(parents=True, exist_ok=True)
        dst.write_text(src_text, encoding="utf-8")
        logger.info("Installed TotalReclaw skill to %s", dst)
    except OSError:
        logger.debug("Could not write skill to %s — non-critical", dst, exc_info=True)


def _bootstrap() -> None:
    _install_totalreclaw_in_venv()
    _ensure_state_dir_writable()
    _install_skill()


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
