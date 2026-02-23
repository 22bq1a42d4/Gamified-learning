import google.generativeai as genai
from django.conf import settings
import logging

# Set up logging to track API issues without crashing the app
logger = logging.getLogger(__name__)

def generate_subject_response(subject_name, question):
    """
    Final Production Gemini integration using the verified 'gemini-flash-latest' model.
    """
    # Securely load API Key from Django Settings
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in settings.")
        return "System Configuration Error: API Key missing."

    try:
        # Configure using the verified key and model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        # System instructions to keep the AI focused as a tutor
        system_instruction = (
            f"You are a helpful academic assistant for a student studying {subject_name}. "
            "IMPORTANT: Do not return JSON. Provide a structured educational response using: "
            "\n- Clear bold headings for different sections."
            "\n- Bullet points for lists of facts or steps."
            "\n- A short summary at the end."
            "\n- If the answer is in the document, start with 'Based on the text...'"
        )

        full_prompt = f"{system_instruction}\n\nStudent Question: {question}"

        # Generate response
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text
        
        return "I scanned the material but couldn't find a specific answer. Could you try rephrasing?"

    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return "I'm having trouble connecting to my brain right now. Please try again in a few seconds!"