from __future__ import annotations

import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()


class LLMInterface:
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model

    def ask_llm(self, prompt: str) -> str:
        provider_order = [
            ("openai", os.getenv("OPENAI_API_KEY"), None),
            ("gemini", os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"), "gemini"),
            ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "anthropic"),
            ("groq", os.getenv("GROQ_API_KEY"), "groq"),
            ("grok", os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY"), "grok"),
            ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral"),
            ("openrouter", os.getenv("OPENROUTER_API_KEY"), "openrouter"),
            ("deepseek", os.getenv("DEEPSEEK_API_KEY"), "deepseek"),
            ("azure_openai", os.getenv("AZURE_OPENAI_API_KEY"), "azure"),
        ]

        for provider, key, mode in provider_order:
            if not key:
                continue

            try:
                if provider == "gemini":
                    url = (
                        "https://generativelanguage.googleapis.com/v1beta/models/"
                        "gemini-2.5-flash:generateContent?key="
                        f"{key}"
                    )
                    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
                    request = urllib.request.Request(
                        url,
                        data=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(request, timeout=30) as response:
                        payload = json.load(response)
                    candidates = payload.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        texts = [
                            part.get("text", "")
                            for part in parts
                            if isinstance(part, dict) and part.get("text")
                        ]
                        if texts:
                            return "".join(texts)
                    return str(payload)

                if provider in {"groq", "grok", "mistral", "openrouter", "deepseek"}:
                    base_urls = {
                        "groq": "https://api.groq.com/openai/v1",
                        "grok": "https://api.x.ai/v1",
                        "mistral": "https://api.mistral.ai/v1",
                        "openrouter": "https://openrouter.ai/api/v1",
                        "deepseek": "https://api.deepseek.com/v1",
                    }
                    import openai

                    client = openai.OpenAI(api_key=key, base_url=base_urls[provider])
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=250,
                    )
                    return response.choices[0].message.content

                if provider == "azure_openai":
                    import openai

                    client = openai.AzureOpenAI(
                        api_key=key,
                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                    )
                    response = client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", self.model),
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=250,
                    )
                    return response.choices[0].message.content

                if provider == "anthropic":
                    import anthropic

                    client = anthropic.Anthropic(api_key=key)
                    response = client.messages.create(
                        model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                        max_tokens=250,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return "".join(block.text for block in response.content if getattr(block, "text", None))

                import openai

                client = openai.OpenAI(api_key=key)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=250,
                )
                return response.choices[0].message.content
            except Exception as exc:
                return f"LLM request failed: {exc}"

        return "No LLM suggestion available; set one of OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GROK_API_KEY/XAI_API_KEY, MISTRAL_API_KEY, OPENROUTER_API_KEY, DEEPSEEK_API_KEY, or AZURE_OPENAI_API_KEY."
