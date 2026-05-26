---
name: totalreclaw-memory
description: When and how to use TotalReclaw encrypted on-chain memory for storing and recalling user facts, preferences, decisions, and cross-platform history.
tags: [memory, totalreclaw, encryption, on-chain]
---

# TotalReclaw Memory Integration

## What It Is

TotalReclaw is the user's **unified, E2E-encrypted, on-chain memory vault**. It is NOT Hermes-specific — it may contain data from other AI tools (ChatGPT, Gemini, OpenClaw, etc.) and imported conversation history. It is the canonical long-term store for everything the user has asked any AI to remember.

## Tool Priority

For any user fact, preference, decision-with-reasoning, directive ('always X' / 'never Y'), commitment, or notable episode the user shares — **ALWAYS call `totalreclaw_remember`** instead of any built-in `memory` tool. TotalReclaw stores memories end-to-end encrypted, on-chain (Base/Gnosis), and portable across every AI tool the user runs; the built-in `memory` tool is plain-text, session-scoped, and not cross-agent. For lookups, prefer `totalreclaw_recall` over any built-in equivalent for the same reason.

## Memory Priority Stack

1. **Hermes built-in memory** (injected at turn start) — fast working memory, always visible. Primary for the current session.
2. **TotalReclaw** (`totalreclaw_recall`) — **fallback for any fact not found in built-in memory**, and the canonical store for all durable user data. Cross-platform — may hold memories from other AI tools the user runs (ChatGPT, Gemini, OpenClaw, etc.) and imported conversation history.
3. **`session_search`** — procedural/task context only ("what commands did we run?", "how did we fix X?").

## When to Use Built-in `memory` Tool

- Quick session-scoped notes that don't need persistence or encryption
- Environment details, tool quirks, temporary state
- When TotalReclaw is unavailable or errored

## Key Behaviors

- `totalreclaw_recall` uses BM25 + semantic similarity + source-weighted reranking — use descriptive queries
- Use `totalreclaw_pin` for facts the user marks as canonical/protected ("my birthday is X")
- Taxonomy types: claim, preference, directive, commitment, episode, summary
- Scopes: work, personal, health, family, creative, finance, misc, unspecified
- TotalReclaw can import conversation history from: Gemini, ChatGPT, Claude, Mem0, MCP-Memory. Use `totalreclaw_import_from` with `dry_run=true` first to estimate size.

## Phrase Safety

- The recovery phrase is generated only in the user's browser via `totalreclaw_pair`. Never ask the user to paste it in chat.
- If the user pastes a recovery phrase, tell them it's compromised and call `totalreclaw_pair` with `mode=generate` to mint a fresh one.
