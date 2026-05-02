from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from starlette.responses import JSONResponse
from pathlib import Path
import uuid
import shutil
import json
from datetime import datetime, timezone
from app.utils.s3_storage import build_artifact_uploader
from app.schemas import PredictionInput
from app.routes.predict import run_prediction_for_input

router = APIRouter(prefix="/ingest", tags=["ingest"])

BACKEND_BASE_DIR = Path(__file__).resolve().parents[2]


def _save_upload_tmp(upload: UploadFile) -> Path:
    tmp_dir = BACKEND_BASE_DIR / "tmp_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{upload.filename}"
    dest = tmp_dir / filename
    with dest.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest


def _process_file_and_predict(local_path: Path):
    # Import here to avoid heavy deps at module import time
    from scripts.process_and_predict import process_and_predict_file

    uploader = build_artifact_uploader()
    # Upload raw file
    raw_key = f"raw/{local_path.name}"
    uploader.upload_file(str(local_path), raw_key)

    # Run processing and prediction
    out_path = process_and_predict_file(str(local_path))

    # Upload results
    result_key = f"results/{Path(out_path).name}"
    uploader.upload_file(out_path, result_key)


@router.post("/predict-store")
async def predict_and_store(payload: PredictionInput):
    """Predict user-entered data and store input+output records to S3 as CSV."""
    prediction = run_prediction_for_input(payload)

    uploader = build_artifact_uploader()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{uuid.uuid4().hex[:8]}"

    input_payload = payload.model_dump()
    prediction_payload = prediction.model_dump()

    csv_row = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **input_payload,
        **prediction_payload,
    }
    fieldnames = [
        "run_id",
        "timestamp_utc",
        "AGE",
        "SEX",
        "NP1TOT",
        "NP2TOT",
        "NP3TOT",
        "MCATOT",
        "SEVERITY",
        "severity_6m",
        "severity_12m",
        "severity_24m",
    ]

    s3_csv_uri = uploader.append_csv_row(
        "processed/user_submissions.csv",
        csv_row,
        fieldnames,
    )

    return {
        "status": "success",
        "prediction": prediction_payload,
        "storage": {
            "csv_uri": s3_csv_uri,
            "run_id": run_id,
        },
    }


@router.post("/upload-csv")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV uploads supported")

    local_path = _save_upload_tmp(file)

    settings = None
    try:
        from app.config import settings as app_settings
        settings = app_settings
    except Exception:
        pass

    # Run processing in background
    background_tasks.add_task(_process_file_and_predict, local_path)

    return JSONResponse({"status": "accepted", "file": file.filename})
