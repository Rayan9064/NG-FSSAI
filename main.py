"""
NutriGrade - Nutrition Intelligence Platform
FastAPI backend for FSSAI compliance checking using Open Food Facts data.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse, IngredientDetail
from off_client import OpenFoodFactsClient
from fssai_kb import FSSAIKnowledgeBase
from analyzer import IngredientsAnalyzer

# Global instances
fssai_kb = FSSAIKnowledgeBase()
off_client = None
analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    global off_client, analyzer
    
    # Load FSSAI knowledge base
    fssai_kb.load()
    
    # Initialize clients
    off_client = OpenFoodFactsClient()
    analyzer = IngredientsAnalyzer(fssai_kb)
    
    yield
    
    # Shutdown
    await off_client.close()


app = FastAPI(
    title="NutriGrade API",
    description="FSSAI compliance checking for food products",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_product(request: AnalyzeRequest):
    """
    Analyze a food product for FSSAI compliance.
    
    Accepts either a barcode (to fetch from Open Food Facts) or 
    direct ingredients text.
    """
    product_name = None
    ingredients_text = None
    source = "manual"
    
    # If barcode is provided, fetch from Open Food Facts
    if request.barcode:
        product_data = await off_client.get_product_by_barcode(request.barcode)
        
        if not product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Product with barcode {request.barcode} not found in Open Food Facts"
            )
        
        # Extract ingredients text
        ingredients_text = off_client.extract_ingredients_text(product_data)
        
        if not ingredients_text:
            raise HTTPException(
                status_code=404,
                detail=f"No ingredients text found for product {request.barcode}"
            )
        
        # Extract product name
        product_name = off_client.get_product_name(product_data)
        source = "openfoodfacts"
    
    # If ingredients_text is provided directly, use it
    if request.ingredients_text:
        ingredients_text = request.ingredients_text
        source = "manual"
    
    # Validate we have ingredients text
    if not ingredients_text:
        raise HTTPException(
            status_code=400,
            detail="No ingredients text available for analysis"
        )
    
    # Analyze ingredients
    ingredients, product_compliance = analyzer.analyze_ingredients_text(ingredients_text)
    
    return AnalyzeResponse(
        product_name=product_name,
        source=source,
        ingredients_text=ingredients_text,
        ingredients=ingredients,
        product_compliance=product_compliance
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
