import os
import requests
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import Literal

load_dotenv()
TIMEOUT = 120  # the large NVIDIA model can take over a minute while it reasons
DEFAULT_PROVIDER = "nvidia"
GEMINI_MODEL = "gemini-3.8-flash"  # confirma el vigente en ai.google.dev/gemini-api/docs/models
NVIDIA_MODEL = "mistralai/mistral-large-4-1t-a52b"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

class Opinion(BaseModel):
    entity: str
    sentiment: Literal["positive", "neutral", "negative"]
    reason: str

class Opinions(BaseModel):
    opinions: list[Opinion]

class Summary(BaseModel):
    summary: str

def gemini_chat(prompt: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={"timeout": TIMEOUT * 1000})
    r = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
            "thinking_config": {"thinking_budget": 0},
        },
    )
    return r.text

def nvidia_chat(prompt: str) -> str:
    r = requests.post(
        NVIDIA_URL,
        headers={"Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}", "Accept": "application/json"},
        json={
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,  # the model reasons first; a low limit leaves no room for the answer
            "temperature": 0,
            "reasoning_effort": "low",  # lowest value this model accepts ("none" is rejected)
            "stream": False,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    choice = r.json()["choices"][0]
    if not choice["message"]["content"]:
        raise RuntimeError(f"empty answer (finish_reason={choice['finish_reason']})")
    return choice["message"]["content"]

# provider name -> (env var with its key, function that calls it)
PROVIDERS = {
    "nvidia": ("NVIDIA_API_KEY", nvidia_chat),
    "gemini": ("GEMINI_API_KEY", gemini_chat),
}

def chat(prompt: str, provider: str | None = None) -> str:
    provider = provider or DEFAULT_PROVIDER
    names = [name for name, (key, _) in PROVIDERS.items() if os.getenv(key)]
    if provider in names:
        names.remove(provider)
        names.insert(0, provider)
    if not names:
        raise RuntimeError("No LLM api key found in .env")
    for name in names:
        try:
            return PROVIDERS[name][1](prompt)
        except Exception as e:
            print(f"\n{name} failed: {e}")
    raise RuntimeError("All LLM providers failed")

def only_json(text: str) -> str:
    # some models wrap the answer in ```json fences
    return text[text.index("{"): text.rindex("}") + 1]

def summarize(text: str, provider: str | None = None) -> str:
    prompt = (
        "Summarize the article in 2 sentences. Use only what the article says.\n\n"
        'Answer ONLY with JSON: {"summary": "..."}\n\n'
        f"Article:\n{text}"
    )
    return Summary.model_validate_json(only_json(chat(prompt, provider))).summary

def entity_sentiments(text: str, entities: list[str], provider: str | None = None) -> list[Opinion]:
    prompt = (
        "For each entity below, say whether the article portrays it positively, neutrally or negatively, "
        "with a short reason (max 15 words). Judge only what the article says, not your own opinion. "
        "Some entities may be the same one under different names (e.g. 'Starmer' and 'Keir Starmer'): "
        "merge them into one using the most complete name.\n\n"
        'Answer ONLY with JSON: {"opinions": [{"entity": "...", "sentiment": "positive|neutral|negative", "reason": "..."}]}\n\n'
        f"Entities: {', '.join(entities)}\n\nArticle:\n{text}"
    )
    return Opinions.model_validate_json(only_json(chat(prompt, provider))).opinions
