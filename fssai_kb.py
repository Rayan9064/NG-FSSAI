"""
FSSAI knowledge base loader and query functions.
"""
import json
from pathlib import Path
from typing import Optional


class FSSAIKnowledgeBase:
    """FSSAI additives knowledge base."""
    
    def __init__(self, data_path: str = "data/fssai_additives.json"):
        """
        Initialize the knowledge base.
        
        Args:
            data_path: Path to the FSSAI additives JSON file
        """
        self.data_path = Path(data_path)
        self.additives = {}
        self.name_to_ins = {}
        self.loaded = False
    
    def load(self):
        """Load the FSSAI additives data from JSON file."""
        if not self.data_path.exists():
            print(f"Warning: FSSAI data file not found at {self.data_path}")
            self.loaded = True
            return
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Build indexes for fast lookup
            for additive in data:
                ins_number = additive.get("ins_number")
                name = additive.get("name", "").lower()
                
                if ins_number:
                    self.additives[ins_number] = additive
                
                if name:
                    self.name_to_ins[name] = ins_number
            
            self.loaded = True
            print(f"Loaded {len(self.additives)} FSSAI additives")
            
        except Exception as e:
            print(f"Error loading FSSAI data: {e}")
            self.loaded = True
    
    def lookup_by_ins(self, ins_number: str) -> Optional[dict]:
        """
        Lookup additive by INS number.
        
        Args:
            ins_number: INS number (e.g., "211")
        
        Returns:
            Additive data dict or None
        """
        if not self.loaded:
            self.load()
        
        return self.additives.get(ins_number)
    
    def lookup_by_name(self, name: str) -> Optional[dict]:
        """
        Lookup additive by name.
        
        Args:
            name: Additive name (case-insensitive)
        
        Returns:
            Additive data dict or None
        """
        if not self.loaded:
            self.load()
        
        name_lower = name.lower()
        ins_number = self.name_to_ins.get(name_lower)
        
        if ins_number:
            return self.additives.get(ins_number)
        
        return None
    
    def get_all_additives(self) -> dict:
        """
        Get all additives in the knowledge base.
        
        Returns:
            Dict mapping INS numbers to additive data
        """
        if not self.loaded:
            self.load()
        
        return self.additives
