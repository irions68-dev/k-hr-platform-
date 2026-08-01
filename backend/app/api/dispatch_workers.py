from __future__ import annotations

import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import excel_io, rule_checker
from app.models.dispatch_worker import DispatchWorker
from app.schemas.dispatch_worker import (
    DispatchWorkerCreate,
    DispatchWorkerOut,
    DispatchWorkerRiskOut,
    ExcelImportResult,
)

router = APIRouter(prefix="/dispatch-workers", tags=["dispatch-workers"])


@router.post("", response_model=DispatchWorkerOut)
def create_worker(
    payload: DispatchWorkerCreate, db: Session = Depends(get_db)
) -> DispatchWorker:
    worker = DispatchWorker(**payload.model_dump())
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.get("", response_model=list[DispatchWorkerRiskOut])
def list_workers(db: Session = Depends(get_db)) -> list[dict]:
    workers = db.query(DispatchWorker).all()
    return [_with_risk(w) for w in workers]


@router.post("/import-excel", response_model=ExcelImportResult)
async def import_workers_excel(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> dict:
    content = await file.read()
    records = excel_io.parse_dispatch_workers_excel(content)

    created = []
    for record in records:
        worker = DispatchWorker(**record)
        db.add(worker)
        created.append(worker)
    db.commit()
    for worker in created:
        db.refresh(worker)

    return {"imported_count": len(created), "workers": created}


@router.get("/export-excel")
def export_workers_excel(db: Session = Depends(get_db)) -> StreamingResponse:
    workers = db.query(DispatchWorker).all()
    payload = [
        {
            "name": w.name,
            "position": w.position,
            "contract_start_date": w.contract_start_date,
        }
        for w in workers
    ]
    content = excel_io.export_dispatch_workers_excel(payload)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=dispatch_workers.xlsx"},
    )


def _with_risk(worker: DispatchWorker) -> dict:
    expiration = rule_checker.check_dispatch_expiration(worker.contract_start_date)
    return {
        "id": worker.id,
        "name": worker.name,
        "position": worker.position,
        "contract_start_date": worker.contract_start_date,
        "created_at": worker.created_at,
        "limit_date": expiration["limit_date"],
        "d_day": expiration["d_day"],
        "status": expiration["status"],
    }
