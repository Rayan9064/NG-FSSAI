# NutriGrade - FSSAI Compliance API

A FastAPI-based backend service for checking food product compliance with FSSAI (Food Safety and Standards Authority of India) regulations.

## Features

- ✅ Analyze food products by barcode (via Open Food Facts API)
- ✅ Analyze products by ingredients text
- ✅ Extract INS/E-numbers from ingredients
- ✅ Check FSSAI compliance status
- ✅ Determine overall product compliance level

## Project Structure

```
nutrigrade-model/
├── main.py              # FastAPI application and routes
├── models.py            # Pydantic request/response models
├── off_client.py        # Open Food Facts API client
├── fssai_kb.py          # FSSAI knowledge base loader
├── analyzer.py          # Core ingredients analysis logic
├── requirements.txt     # Python dependencies
└── data/
    └── fssai_additives.json  # FSSAI additives database
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rayan9064/NG-FSSAI.git
cd nutrigrade-model
```

2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the development server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### POST /analyze
Analyze a food product for FSSAI compliance.

**Request Body:**
```json
{
  "barcode": "8901063012349",  // Optional: Product barcode
  "ingredients_text": "..."     // Optional: Direct ingredients text
}
```

Note: At least one of `barcode` or `ingredients_text` must be provided.

**Response:**
```json
{
  "product_name": "Sample Product",
  "source": "openfoodfacts",
  "ingredients_text": "Water, Sugar, INS 211 (Sodium benzoate)...",
  "ingredients": [
    {
      "raw": "INS 211",
      "normalized_ins": "211",
      "name": "Sodium benzoate",
      "status": "permitted",
      "max_ppm": 500,
      "allowed_in": ["non-alcoholic beverages", "jams"],
      "notes": "Not allowed in meat/fish products"
    }
  ],
  "product_compliance": "compliant"
}
```

## Compliance Status

- **compliant**: All additives are permitted
- **partially_compliant**: Contains restricted additives
- **non_compliant**: Contains banned additives
- **unknown**: Contains additives not in FSSAI database

## Example Usage

### Analyze by barcode:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"barcode": "8901063012349"}'
```

### Analyze by ingredients text:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ingredients_text": "Water, Sugar, INS 211, INS 621"}'
```

## Development

The FSSAI additives database is stored in `data/fssai_additives.json`. You can add more additives following the schema:

```json
{
  "ins_number": "211",
  "name": "Sodium benzoate",
  "status": "permitted",
  "max_ppm": 500,
  "allowed_in": ["category1", "category2"],
  "notes": "Additional information"
}
```

## Tech Stack

- **Python 3.11+**
- **FastAPI**: Modern web framework
- **Pydantic**: Data validation
- **httpx**: Async HTTP client for Open Food Facts API
- **uvicorn**: ASGI server

## License

MIT
