# Netra Vision

AI-powered crop disease detection. Upload a photo of a plant/crop and get back a
structured disease diagnosis and treatment plan, powered by Google Gemini vision.

## Requirements

- Python 3.12+
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

## Run

```bash
cd app
uvicorn main:app --reload
```

The API is served at `http://127.0.0.1:8000`, with interactive docs at
`http://127.0.0.1:8000/docs`.

## API

### `POST /analyse/`

Upload a single image (`multipart/form-data`, field name `file`) for disease
detection.

- Accepted types: `image/jpeg`, `image/png`
- Max size: 15 MB
- Images larger than 2048px (longest side) are downscaled before analysis

**Response**

```json
{
  "id": "40603e83d3274ce1a0cfb84c6cec457e",
  "filename": "leaf.jpg",
  "content_type": "image/jpeg",
  "message": "Image received and processed for disease detection.",
  "result": {
    "crop_detected": "Apple (Malus domestica)",
    "severity": "severe",
    "diseases": [
      {
        "name": "Apple Leaf Blight",
        "confidence": 0.88,
        "description": "..."
      }
    ],
    "treatments": [
      {
        "treatment_name": "Fungicide Spray",
        "treatment_type": "chemical",
        "instructions": "...",
        "urgency": "immediate"
      }
    ],
    "overall_health": "...",
    "additional_notes": "..."
  }
}
```

### `POST /analyse/batch`

Upload multiple images (`multipart/form-data`, field name `files`, repeated)
for batch disease detection. Each file is validated and analysed
independently — one failing file doesn't fail the rest.

**Response**

```json
{
  "count": 3,
  "results": [
    { "status": "success", "id": "...", "filename": "leaf1.jpg", "content_type": "image/jpeg", "result": { "...": "..." } },
    { "status": "success", "id": "...", "filename": "leaf2.jpg", "content_type": "image/jpeg", "result": { "...": "..." } },
    { "status": "error", "filename": "notes.txt", "content_type": "text/plain", "error": "Invalid file type. Please upload an image." }
  ]
}
```

### `GET /analyses/`

Retrieve every analysis performed so far (single and batch), most recent
first.

### `GET /analyses/{analysis_id}`

Retrieve one analysis record by id. Returns `404` if the id doesn't exist.

## Project structure

```
app/
  main.py                    # FastAPI app entrypoint
  routes/
    analyse_router.py        # /analyse, /analyse/batch, /analyses routes
  services/
    image.py                 # Validation, resizing, saving of uploaded images
    vision.py                # Gemini call + disease-analysis prompt
    storage.py                # Persists/reads analysis records as JSON files
  uploads/                   # Saved uploads (gitignored)
  analyses/                  # Saved analysis records (gitignored)
```

## Notes

- Uploaded images are saved to `app/uploads/` with a generated UUID filename;
  the same id is used as the analysis id.
- Each analysis (single or batch) is persisted to `app/analyses/<id>.json`
  so it can be listed/retrieved later via `GET /analyses`.
- Vision analysis calls `gemini-3.6-flash` via `google-genai`, with a 30s
  request timeout.
