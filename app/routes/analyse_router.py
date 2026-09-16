import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from services.image import validate_image, resize_image_if_needed, save_image
from services.vision import analyse_image as vision_analyse_image
from services.storage import save_analysis, get_analysis, list_analyses

analyse_router = APIRouter(prefix="/analyse", tags=["Analyse"])
analyses_router = APIRouter(prefix="/analyses", tags=["Analyses"])


async def process_single_image(file: UploadFile) -> dict:
    """
    Process a single image for disease detection and persist the result.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image.",
        )

    content = await file.read()

    validation = validate_image(content, file.content_type)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=validation["message"]
        )

    processed = resize_image_if_needed(content)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    analysis_id = uuid.uuid4().hex
    unique_name = f"{analysis_id}.{ext}"

    path = save_image(processed, "uploads", unique_name)
    result = await vision_analyse_image(path, file.content_type)

    record = {
        "id": analysis_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    save_analysis(record)

    return record


@analyse_router.post("/")
async def analyse_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image for disease detection.
    """
    record = await process_single_image(file)

    return {
        "id": record["id"],
        "filename": record["filename"],
        "result": record["result"],
        "content_type": record["content_type"],
        "message": "Image received and processed for disease detection.",
    }


@analyse_router.post("/batch")
async def analyse_batch(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload multiple images for batch disease detection.
    """
    results = []

    for file in files:
        try:
            record = await process_single_image(file)
            results.append(
                {
                    "id": record["id"],
                    "filename": record["filename"],
                    "content_type": record["content_type"],
                    "result": record["result"],
                    "status": "success",
                }
            )
        except HTTPException as exc:
            results.append(
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "status": "error",
                    "error": exc.detail,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "status": "error",
                    "error": f"Analysis failed: {exc}",
                }
            )

    return {"count": len(results), "results": results}


@analyses_router.get("/")
async def get_analyses():
    """
    Retrieve a list of all analyses performed.
    """
    return list_analyses()


@analyses_router.get("/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """
    Retrieve details of a specific analysis by ID.
    """
    record = get_analysis(analysis_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found"
        )
    return record
