"""Provider adapters for the oversight pass. Standard library only.

Each exposes review(prompt, api_key, cfg) -> str.

Adding one: write the function, add it to ADAPTERS. The prompt is provider
agnostic, so an adapter is only request shape and response unwrapping.
"""
import json, urllib.request


def _post(url, payload, headers, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class anthropic:
    @staticmethod
    def review(prompt, key, cfg):
        d = _post("https://api.anthropic.com/v1/messages",
                  {"model": cfg.get("model", "claude-sonnet-5"),
                   "max_tokens": cfg.get("max_tokens", 4000),
                   "messages": [{"role": "user", "content": prompt}]},
                  {"x-api-key": key, "anthropic-version": "2023-06-01"})
        return "".join(b.get("text", "") for b in d.get("content", []))


class openai:
    @staticmethod
    def review(prompt, key, cfg):
        d = _post("https://api.openai.com/v1/chat/completions",
                  {"model": cfg.get("model", "gpt-4o"),
                   "max_tokens": cfg.get("max_tokens", 4000),
                   "messages": [{"role": "user", "content": prompt}]},
                  {"authorization": f"Bearer {key}"})
        return d["choices"][0]["message"]["content"]


class google:
    @staticmethod
    def review(prompt, key, cfg):
        model = cfg.get("model", "gemini-2.0-flash")
        d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                  {"contents": [{"parts": [{"text": prompt}]}]}, {})
        return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])


ADAPTERS = {"anthropic": anthropic, "openai": openai, "google": google}
