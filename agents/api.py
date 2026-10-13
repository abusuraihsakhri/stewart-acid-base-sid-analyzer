"""
FastAPI REST API Server for Stewart Acid Base Sid Analyzer.
"""
from pathlib import Path
from fastapi.responses import FileResponse
from stewart_sid import calculate_metrics
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Stewart Acid Base Sid Analyzer API",
    description="Stewart–Figge calculation API with separate legacy demonstration audit endpoints",
    version="3.0.0-ENTERPRISE",
)


class CalculationRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")
    sodium: float
    potassium: float
    ionized_calcium: float
    ionized_magnesium: float
    chloride: float
    lactate: float
    ph: float
    pco2: float
    albumin: float
    phosphate: float


class ChatRequest(BaseModel):
    query: str


@app.get("/", include_in_schema=False)
def browser_app():
    return FileResponse(Path(__file__).resolve().parent.parent / "index.html")


@app.post("/api/calculate")
def api_calculate(payload: CalculationRequest):
    try:
        return calculate_metrics(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "stewart-acid-base-sid-analyzer", "domain": "Clinical & Biomedical AI", "standard": "Stewart–Figge research equations", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
