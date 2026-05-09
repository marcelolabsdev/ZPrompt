import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from services.openai_service import generate_prompt
from services.templates import TEMPLATE_DESCRIPTIONS, TEMPLATE_LABELS

load_dotenv()

app = FastAPI(
    title="ZPrompt",
    description="Generador de prompts estructurados para desarrollo de software",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    prompt_type: str = Field(..., pattern="^(system|start|followup|research|debug)$")
    language: str | None = None
    framework: str | None = None


class PromptResponse(BaseModel):
    prompt: str
    prompt_type: str
    label: str
    timestamp: str


@app.get("/api/debug")
def debug_filesystem():
    cwd = os.getcwd()
    file_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_check = [
        os.path.join(cwd, "public"),
        os.path.join(file_dir, "public"),
        os.path.join(file_dir, "..", "public"),
        "/var/task/public",
        "/var/task/user/public",
    ]
    results = {
        "cwd": cwd,
        "file_dir": file_dir,
        "cwd_files": os.listdir(cwd) if os.path.exists(cwd) else [],
        "path_checks": {},
    }
    for p in paths_to_check:
        results["path_checks"][p] = {
            "exists": os.path.exists(p),
            "files": os.listdir(p) if os.path.exists(p) else [],
        }
    return results


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    paths = [
        os.path.join(os.getcwd(), "public", "favicon.ico"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "favicon.ico"),
    ]
    for p in paths:
        if os.path.exists(p):
            return FileResponse(p)
    raise HTTPException(status_code=404)


@app.get("/")
def serve_index():
    paths = [
        os.path.join(os.getcwd(), "public", "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>ZPrompt</h1><p>Frontend no encontrado. Visita <a href='/api/debug'>/api/debug</a> para diagnosticar.</p>")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/templates")
def get_templates():
    result = []
    for key, label in TEMPLATE_LABELS.items():
        result.append(
            {
                "id": key,
                "label": label,
                "description": TEMPLATE_DESCRIPTIONS.get(key, ""),
            }
        )
    return {"templates": result}


@app.post("/api/generate", response_model=PromptResponse)
async def create_prompt(request: PromptRequest):
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY no configurada. Agregala como variable de entorno.",
        )

    try:
        prompt_text = await generate_prompt(
            text=request.text,
            prompt_type=request.prompt_type,
            language=request.language,
            framework=request.framework,
        )
        return PromptResponse(
            prompt=prompt_text,
            prompt_type=request.prompt_type,
            label=TEMPLATE_LABELS.get(request.prompt_type, ""),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generando prompt: {str(e)}"
        )


@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300},
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z",
    }
