"""
Open Food Facts API client.
"""
import httpx
from typing import Optional


class OpenFoodFactsClient:
    """Client for interacting with Open Food Facts API."""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_product_by_barcode(self, barcode: str) -> Optional[dict]:
        """
        Fetch product details from Open Food Facts by barcode.
        
        Args:
            barcode: Product barcode (e.g., "8901063012349")
        
        Returns:
            Product data dict or None if not found
        """
        try:
            url = f"{self.BASE_URL}/product/{barcode}.json"
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if product was found
            if data.get("status") == 1 and "product" in data:
                return data["product"]
            
            return None
            
        except httpx.HTTPError as e:
            print(f"HTTP error fetching product {barcode}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching product {barcode}: {e}")
            return None
    
    def extract_ingredients_text(self, product_data: dict) -> Optional[str]:
        """
        Extract ingredients text from Open Food Facts product data.
        
        Args:
            product_data: Product dict from OFF API
        
        Returns:
            Ingredients text string or None
        """
        # Try different possible fields
        ingredients_text = (
            product_data.get("ingredients_text_en") or
            product_data.get("ingredients_text") or
            product_data.get("ingredients_text_with_allergens_en")
        )
        
        return ingredients_text if ingredients_text else None
    
    def get_product_name(self, product_data: dict) -> Optional[str]:
        """
        Extract product name from Open Food Facts product data.
        
        Args:
            product_data: Product dict from OFF API
        
        Returns:
            Product name or None
        """
        return (
            product_data.get("product_name_en") or
            product_data.get("product_name") or
            None
        )
