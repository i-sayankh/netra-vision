import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

REQUEST_TIMEOUT_MS = 30_000


CROP_ANALYSIS_PROMPT = """
    You are an expert agricultural scientist specializing in crop disease detection.
Analyze this image of a crop/plant and provide a detailed disease assessment.

Provide your analysis as a JSON object with exactly this structure:

{
"crop_detected": "Name of the crop or plant visible in the image",
"severity": "healthy" or "mild" or "moderate" or "severe" or "critical",
"diseases": [
        {
            "name": "Disease name",
            "confidence": 0.0 to 1.0,
            "description": "Brief description of the disease and visible symptoms"
        }
    ],
"treatments": [
        {
            "treatment_name": "Name of treatment",
            "treatment_type": "organic" or "chemical" or "preventive",
            "instructions": "Step by step treatment instructions",
            "urgency": "immediate" or "within_week" or "seasonal"
        }
    ],
    "overall_health": "One sentence summary of plant health",
    "additional_notes": "Any other observations or recommendations"
}
"""


async def analyse_image(image_path: str, content_type: str):
    """
    Analyse the image content using Google GenAI for disease detection.
    """

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            CROP_ANALYSIS_PROMPT,
            types.Part.from_bytes(data=image_bytes, mime_type=content_type),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
        ),
    )

    print(f"Raw response from GenAI: {response.text}")
    return json.loads(response.text)
