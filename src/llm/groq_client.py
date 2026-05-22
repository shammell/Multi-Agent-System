import os

from groq import Groq


class GroqLLMClient:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile") -> None:
        self.client = Groq(api_key=api_key)
        self.model = model

    async def complete(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""


def build_live_client_from_env():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY missing in environment")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return GroqLLMClient(api_key=api_key, model=model)
