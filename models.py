"""
Pydantic models for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, field_validator


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint."""
    barcode: Optional[str] = None
    ingredients_text: Optional[str] = None

    @field_validator('barcode', 'ingredients_text')
    @classmethod
    def at_least_one_field(cls, v, info):
        """Ensure at least one of barcode or ingredients_text is provided."""
        return v

    def model_post_init(self, __context):
        """Validate that at least one field is provided."""
        if not self.barcode and not self.ingredients_text:
            raise ValueError("At least one of 'barcode' or 'ingredients_text' must be provided")


class IngredientDetail(BaseModel):
    """Details about a single ingredient/additive."""
    raw: str
    normalized_ins: Optional[str] = None
    name: Optional[str] = None
    status: str = "unknown"  # permitted | restricted | banned | unknown
    max_ppm: Optional[int] = None
    allowed_in: Optional[list[str]] = None
    notes: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response model for /analyze endpoint."""
    product_name: Optional[str] = None
    source: str  # openfoodfacts | manual
    ingredients_text: str
    ingredients: list[IngredientDetail]
    product_compliance: str  # compliant | partially_compliant | non_compliant | unknown
