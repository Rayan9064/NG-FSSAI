"""
Core analysis logic for extracting and evaluating additives.
"""
import re
from typing import List, Tuple
from models import IngredientDetail
from fssai_kb import FSSAIKnowledgeBase


class IngredientsAnalyzer:
    """Analyzer for extracting additives and evaluating FSSAI compliance."""
    
    def __init__(self, fssai_kb: FSSAIKnowledgeBase):
        """
        Initialize the analyzer.
        
        Args:
            fssai_kb: FSSAI knowledge base instance
        """
        self.fssai_kb = fssai_kb
    
    def extract_additives(self, ingredients_text: str) -> List[Tuple[str, str]]:
        """
        Extract additives from ingredients text.
        
        Args:
            ingredients_text: Raw ingredients text string
        
        Returns:
            List of tuples (raw_match, normalized_ins)
        """
        additives = []
        
        # Pattern for INS numbers: INS 211, INS-211, INS211, (INS 211), etc.
        ins_pattern = r'(?:INS[\s-]?(\d{3,4})(?:\s*\([^)]+\))?)'
        
        for match in re.finditer(ins_pattern, ingredients_text, re.IGNORECASE):
            raw_match = match.group(0)
            ins_number = match.group(1)
            additives.append((raw_match, ins_number))
        
        # Pattern for E-numbers: E211, E-211, (E211), etc.
        e_pattern = r'(?:E[\s-]?(\d{3,4})(?:\s*\([^)]+\))?)'
        
        for match in re.finditer(e_pattern, ingredients_text, re.IGNORECASE):
            raw_match = match.group(0)
            e_number = match.group(1)
            # E-numbers often map to INS numbers (same numbering)
            additives.append((raw_match, e_number))
        
        return additives
    
    def analyze_ingredient(self, raw: str, ins_number: str) -> IngredientDetail:
        """
        Analyze a single ingredient/additive.
        
        Args:
            raw: Raw matched text (e.g., "INS 211")
            ins_number: Normalized INS number (e.g., "211")
        
        Returns:
            IngredientDetail with FSSAI compliance info
        """
        # Lookup in FSSAI knowledge base
        fssai_data = self.fssai_kb.lookup_by_ins(ins_number)
        
        if fssai_data:
            return IngredientDetail(
                raw=raw,
                normalized_ins=ins_number,
                name=fssai_data.get("name"),
                status=fssai_data.get("status", "unknown"),
                max_ppm=fssai_data.get("max_ppm"),
                allowed_in=fssai_data.get("allowed_in"),
                notes=fssai_data.get("notes")
            )
        else:
            # Not found in KB
            return IngredientDetail(
                raw=raw,
                normalized_ins=ins_number,
                status="unknown"
            )
    
    def analyze_ingredients_text(self, ingredients_text: str) -> Tuple[List[IngredientDetail], str]:
        """
        Analyze ingredients text and determine product compliance.
        
        Args:
            ingredients_text: Raw ingredients text
        
        Returns:
            Tuple of (list of IngredientDetails, product_compliance status)
        """
        # Extract additives
        raw_additives = self.extract_additives(ingredients_text)
        
        # Analyze each additive
        ingredients = []
        for raw, ins_number in raw_additives:
            detail = self.analyze_ingredient(raw, ins_number)
            ingredients.append(detail)
        
        # Determine overall product compliance
        product_compliance = self._determine_product_compliance(ingredients)
        
        return ingredients, product_compliance
    
    def _determine_product_compliance(self, ingredients: List[IngredientDetail]) -> str:
        """
        Determine overall product compliance based on ingredient statuses.
        
        Args:
            ingredients: List of analyzed ingredients
        
        Returns:
            Compliance status: compliant | partially_compliant | non_compliant | unknown
        """
        if not ingredients:
            return "unknown"
        
        has_banned = False
        has_restricted = False
        has_unknown = False
        has_permitted = False
        
        for ingredient in ingredients:
            status = ingredient.status.lower()
            if status == "banned":
                has_banned = True
            elif status == "restricted":
                has_restricted = True
            elif status == "unknown":
                has_unknown = True
            elif status == "permitted":
                has_permitted = True
        
        # Decision logic
        if has_banned:
            return "non_compliant"
        elif has_restricted:
            return "partially_compliant"
        elif has_unknown:
            return "unknown"
        elif has_permitted:
            return "compliant"
        else:
            return "unknown"
