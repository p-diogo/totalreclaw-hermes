TotalReclaw Hermes plugin installed.

Next steps:
  1. Install the backing Python package (if not already): pip install --pre totalreclaw
  2. Restart the gateway: hermes gateway restart
  3. Paste this into your chat: "Set up TotalReclaw"
  4. The agent will give you a URL + 6-digit PIN. Open the URL, enter your recovery phrase in the browser, confirm the PIN.
  5. Done — try "remember X" and "recall what I said about X" in future conversations.

Your recovery phrase never crosses the LLM context — it's encrypted browser-side.

Docs: https://github.com/p-diogo/totalreclaw/blob/main/docs/guides/hermes-setup.md
