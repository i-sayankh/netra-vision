import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from services.image import validate_image, resize_image_if_needed, save_image
from services.vision import analyse_image as vision_analyse_image

analyse_router = APIRouter(prefix="/analyse", tags=["Analyse"])


async def process_single_image(file: UploadFile):
    """
    Process a single image for disease detection.
    """

    content = await file.read()

    validation = validate_image(content, file.content_type)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=validation["message"]
        )

    processed = resize_image_if_needed(content)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    path = save_image(processed, "uploads", unique_name)
    result = await vision_analyse_image(path, file.content_type)

    return result


@analyse_router.post("/")
async def analyse_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image for disease detection.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image.",
        )

    result = await process_single_image(file)

    return {
        "filename": file.filename,
        "result": result,
        "content_type": file.content_type,
        "message": "Image received and processed for disease detection.",
    }
