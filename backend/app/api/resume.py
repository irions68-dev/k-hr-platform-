from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.engines import resume_extract
from app.schemas.resume import ResumeExtractResult

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/extract", response_model=ResumeExtractResult)
async def extract(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    try:
        return resume_extract.extract_resume(file_bytes, file.content_type or "")
    except resume_extract.UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except resume_extract.FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except resume_extract.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except resume_extract.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
