import json
import os
from difflib import get_close_matches

class MedicalTerminologyValidator:
    def __init__(self):
        self.medical_terms = self._load_medical_terms()

    def _load_medical_terms(self):
        """Load medical terms from JSON file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        terms_file = os.path.join(current_dir, 'data', 'medical_terms.json')
        
        try:
            with open(terms_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading medical terms: {str(e)}")
            return []

    def validate_and_suggest(self, text: str) -> list:
        """
        Validate medical terms in the text and suggest corrections
        Returns a list of suggestions
        """
        words = text.lower().split()
        suggestions = []
        
        for word in words:
            # Check if word is in medical terms
            if word not in self.medical_terms:
                # Find close matches
                matches = get_close_matches(word, self.medical_terms, n=3, cutoff=0.6)
                if matches:
                    suggestions.extend(matches)
        
        return list(set(suggestions))  # Remove duplicates
