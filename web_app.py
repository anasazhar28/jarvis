import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
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


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Add OPENAI_API_KEY in the deployment settings.",
        )
    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


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
    client = get_client()
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n{mode_prompt(request.mode)}"}]
    for item in request.history[-20:]:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"][:12000]})
    messages.append({"role": "user", "content": request.message})
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.7,
            max_tokens=1200,
        )
        answer = response.choices[0].message.content or "I could not generate a response, Sir."
        return {"answer": answer.strip(), "mode": request.mode}
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"AI service error: {error}") from error
