import requests
from typing import Tuple

def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the language of the input text using the Google Cloud Translation API.
    Returns a tuple of (language_code, confidence_score).
    """
    try:
        # For demo purposes, we'll use a simpler approach with the MyMemory API's language detection
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text[:100],  # Use first 100 chars for detection
            'langpair': 'auto|en'  # Target language doesn't matter for detection
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['responseStatus'] == 200:
            detected_lang = data['responseData']['detectedLanguage']
            return detected_lang, 1.0  # MyMemory doesn't provide confidence score
            
        return 'en', 0.0  # Default to English if detection fails
        
    except Exception as e:
        print(f"Language detection error: {str(e)}")
        return 'en', 0.0  # Default to English on error
