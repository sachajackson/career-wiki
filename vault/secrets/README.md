# secrets/ — one file, and it is not this one

**`.env` goes here. Nothing else, ever.**

```
ANTHROPIC_API_KEY=sk-ant-...
```

🔴 **This folder is the one thing in the vault that must not travel.** The rest of the vault is yours to
zip, sync and carry between machines. This is not: a key in a backup is a key in whatever that backup
touches, and an API key that leaks is somebody else's bill and your account.

**`tools/lib/paths.py` classifies this folder as `NEVER`**, which is what stops it being included when
anything bundles a vault. That is a guard against the tools making the mistake. It is not a guard
against you emailing a zip.

## Why a `.env` and not a settings key

**Because a JSON file gets read out loud.** Configuration ends up pasted into a chat window, quoted in a
bug report, or shown on a screen share — and a key sitting in `search.json` between two harmless fields
goes with it. A file that holds only secrets is a file you know not to open in front of anyone.

## If you think a key has leaked

**Revoke it first and worry about how afterwards.** Rotating a key costs a minute; a key that stays live
while you work out whether it really leaked does not.
