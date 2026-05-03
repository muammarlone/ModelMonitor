"""ModelMonitor — ML Model Observability Agent.

Endpoints:
  GET  /health
  POST /api/v1/monitor/analyze   — SVAS drift/performance analysis
  GET  /api/v1/monitor/reports   — past monitoring reports

LLM: OpenRouter. Mock fallback when key absent.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import urllib.error
import urllib.request
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger("ModelMonitor")
logging.basicConfig(level=logging.INFO)

_DB       = os.getenv("MODELMONITOR_DB_PATH", "modelmonitor.db")
_OR_KEY   = os.getenv("OPENROUTER_API_KEY", "")
_OR_BASE  = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
_OR_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

_SYSTEM_PROMPT = """You are ModelMonitor, an ML model observability expert.
Given an intent describing a model monitoring scenario, produce JSON:
{
  "drift_detected": true|false,
  "drift_type": "data|concept|covariate|none",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
  "performance_delta": -0.05,
  "bias_flags": ["demographic_parity", ...],
  "retrain_recommended": true|false,
  "retrain_urgency": "IMMEDIATE|SOON|SCHEDULED|NOT_NEEDED",
  "summary": "...",
  "actions": ["...", "..."]
}
Respond with valid JSON only. Be specific to the model and data domain described."""

_MOCK_REPORT = {
    "drift_detected": True, "drift_type": "data",
    "severity": "MEDIUM", "performance_delta": -0.03,
    "bias_flags": [], "retrain_recommended": True,
    "retrain_urgency": "SOON",
    "summary": "Moderate data drift detected. Feature distribution shifted for 3 key inputs.",
    "actions": ["Collect fresh training data for drifted features",
                "Schedule retraining within 2 weeks",
                "Increase monitoring frequency to daily"],
}


def _init_db():
    conn = sqlite3.connect(_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY, workflow_id TEXT, intent TEXT,
        drift_detected INTEGER, severity TEXT, retrain_recommended INTEGER,
        summary TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit(); conn.close()


def _call_or(intent: str) -> dict:
    payload = json.dumps({
        "model": _OR_MODEL, "max_tokens": 512,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": f"Intent: {intent}"},
        ],
    }).encode()
    req = urllib.request.Request(
        f"{_OR_BASE}/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {_OR_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())
    return json.loads(body["choices"][0]["message"]["content"].strip())


@asynccontextmanager
async def _lifespan(app: FastAPI):
    _init_db(); yield


app = FastAPI(title="ModelMonitor", version="1.0.0", lifespan=_lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class MonitorRequest(BaseModel):
    intent: str
    workflow_id: str = ""
    context: dict = {}
    model_name: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ModelMonitor", "llm_available": bool(_OR_KEY)}


@app.post("/api/v1/monitor/analyze")
def analyze(req: MonitorRequest):
    rid = hashlib.sha256(f"{req.workflow_id}:{req.intent}".encode()).hexdigest()[:12]
    source = "openrouter"
    if _OR_KEY:
        try:
            data = _call_or(req.intent)
        except Exception as exc:
            logger.warning("OR failed (%s) — mock", exc)
            data = {**_MOCK_REPORT, "summary": f"Mock: {req.intent[:100]}"}; source = "mock"
    else:
        data = {**_MOCK_REPORT, "summary": f"Mock: {req.intent[:100]}"}; source = "mock"

    conn = sqlite3.connect(_DB)
    conn.execute("INSERT OR IGNORE INTO reports (id, workflow_id, intent, drift_detected, severity, retrain_recommended, summary) VALUES (?,?,?,?,?,?,?)",
                 (rid, req.workflow_id, req.intent[:200],
                  int(data.get("drift_detected", False)),
                  data.get("severity", "NONE"),
                  int(data.get("retrain_recommended", False)),
                  data.get("summary", "")[:300]))
    conn.commit(); conn.close()

    logger.info("Monitor analyze: id=%s workflow=%s drift=%s", rid, req.workflow_id, data.get("drift_detected"))
    return {"report_id": rid, "workflow_id": req.workflow_id, "source": source, **data}


@app.get("/api/v1/monitor/reports")
def reports(limit: int = 50):
    conn = sqlite3.connect(_DB); conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT id, workflow_id, drift_detected, severity, retrain_recommended, created_at FROM reports ORDER BY created_at DESC LIMIT ?",
        (limit,)).fetchall()]
    conn.close()
    return {"reports": rows, "count": len(rows)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8012")))
