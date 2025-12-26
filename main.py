"""
Context for GitHub Copilot:

I am building a backend service for NutriGrade, a nutrition intelligence platform.
Stack: Python 3.11 + FastAPI. Goal: start with India-focused FSSAI compliance using Open Food Facts data.

High-level flow (v1 MVP):
- Input: either a product barcode OR a raw ingredients text string.
- If barcode is provided:
  - Call Open Food Facts API (v2) to fetch product details.
  - Extract the ingredients text field from the OFF JSON.
- If ingredients_text is provided directly, use it as-is.

- Extract potential additives from ingredients_text:
  - Detect "INS" numbers (e.g., "INS 211", "INS-211").
  - Optionally detect E-numbers (e.g., "E211") and simple additive names.
  - For now this can be done with regex + simple string processing (no ML yet).

- FSSAI knowledge base:
  - I will have a local JSON file: data/fssai_additives.json
  - Example schema for each additive:
    {
      "ins_number": "211",
      "name": "Sodium benzoate",
      "status": "permitted",         # allowed | restricted | banned | unknown
      "max_ppm": 500,
      "allowed_in": ["non-alcoholic beverages", "jams"],
      "notes": "Not allowed in meat/fish products"
    }
  - I want helper functions to:
    - load this JSON at startup
    - lookup by INS code or by name

- Core logic:
  - For each extracted additive:
    - Normalize (e.g., "INS 211" -> "211").
    - Lookup in FSSAI KB.
    - Build a structured result:
      {
        "raw": "INS 211 (Sodium benzoate)",
        "normalized_ins": "211",
        "name": "Sodium benzoate",
        "status": "permitted",
        "max_ppm": 500,
        "allowed_in": [...],
        "notes": "..."
      }
  - Aggregate product-level compliance:
    - If any banned additive -> product_compliance = "non_compliant"
    - Else if any restricted additive -> product_compliance = "partially_compliant"
    - Else if all permitted/unknown -> "compliant" or "unknown" accordingly.

API design:
- FastAPI app with:
  - GET /health -> { "status": "ok" }
  - POST /analyze
    Request body (Pydantic):
      {
        "barcode": Optional[str],
        "ingredients_text": Optional[str]
      }
    - At least one of barcode or ingredients_text must be provided.
    Response body:
      {
        "product_name": Optional[str],
        "source": "openfoodfacts" | "manual",
        "ingredients_text": str,
        "ingredients": [
          {
            "raw": str,
            "normalized_ins": Optional[str],
            "name": Optional[str],
            "status": "permitted" | "restricted" | "banned" | "unknown",
            "max_ppm": Optional[int],
            "allowed_in": Optional[list[str]],
            "notes": Optional[str]
          }
        ],
        "product_compliance": "compliant" | "partially_compliant" | "non_compliant" | "unknown"
      }

What I want Copilot to help with now:
1. Create a minimal FastAPI app structure with:
   - main.py (FastAPI app, routes)
   - models.py (Pydantic request/response models)
   - fssai_kb.py (load and query FSSAI JSON)
   - off_client.py (call Open Food Facts API by barcode)
   - analyzer.py (core logic: ingredients text -> extracted additives -> FSSAI lookups -> result)

2. Implement:
   - The Pydantic models for request and response.
   - A simple OFF client using requests or httpx.
   - Regex-based INS extraction from ingredients_text.
   - FSSAI KB loader and lookup functions.
   - The /analyze endpoint wiring everything together.

Please generate idiomatic, clean, well-structured FastAPI code with type hints.
"""
