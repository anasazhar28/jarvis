import os
from pathlib import Path
import base64
import requests
from io import BytesIO

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

SYSTEM_PROMPT = """
You are J.A.R.V.I.S., a personal AI assistant.
Always address the user as Sir.
Never claim to control the user's computer, access local files, or perform actions you cannot perform through this web app.
Be intelligent, calm, professional, helpful, and slightly witty.
Keep answers natural and reasonably concise.
""".strip()

app = FastAPI(title="J.A.R.V.I.S. Web", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    mode: str = Field(default="jarvis", pattern="^(jarvis|vision|ultron)$")
    history: list[dict[str, str]] = Field(default_factory=list, max_length=30)


def get_groq_response(messages: list[dict]) -> str:
    """Get response from Groq API (free tier available)"""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return "Groq API key not configured. Set GROQ_API_KEY environment variable."
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "mixtral-8x7b-32768",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1200,
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Groq error: {response.status_code}"
    except Exception as e:
        return f"AI service error: {str(e)}"


def get_huggingface_image(prompt: str) -> str:
    """Generate image using HuggingFace Inference API (free)"""
    api_key = os.getenv("HF_API_KEY", "").strip()
    if not api_key:
        return None
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": prompt},
            timeout=60
        )
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
        return None
    except Exception:
        return None


def mode_prompt(mode: str) -> str:
    if mode == "vision":
        return "You are in VISION mode. Explain what the user asks clearly. Image uploads are not enabled in this first web release."
    if mode == "ultron":
        return "You are in ULTRON mode: tactical, concise, analytical, and focused on strategy."
    return "You are in JARVIS mode."


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n{mode_prompt(request.mode)}"}]
    for item in request.history[-20:]:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"][:12000]})
    messages.append({"role": "user", "content": request.message})
    
    answer = get_groq_response(messages)
    if not answer or "error" in answer.lower():
        return {"answer": "AI service temporarily unavailable. Please try again.", "mode": request.mode}
    return {"answer": answer.strip(), "mode": request.mode}


@app.post("/api/generate-image")
def generate_image(request: dict[str, str]) -> dict:
    prompt = request.get("prompt", "").strip()[:1000]
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    image_b64 = get_huggingface_image(prompt)
    if not image_b64:
        raise HTTPException(status_code=503, detail="Image generation service unavailable. Add HF_API_KEY for free HuggingFace Inference API.")
    
    return {"image_data": image_b64, "prompt": prompt}
