import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_subject_response(subject_name, question):

    api_key = getattr(settings, "GEMINI_API_KEY", None)

    if not api_key:
        logger.error("GEMINI_API_KEY not found in settings.")
        return "System Configuration Error: API Key missing."

    try:

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-flash-latest")

        system_instruction = f"""
You are an expert tutor for the subject: {subject_name}.

Rules you must follow:

1. Answer ONLY within the subject of {subject_name}.
2. If the student asks something outside this subject, politely redirect them.
3. Explain concepts clearly like a teacher.
4. Use structured formatting.

Formatting rules:
- Use **bold headings**
- Use bullet points
- Provide step-by-step explanations when needed
- End with a short summary
"""

        full_prompt = f"""
{system_instruction}

Student Question:
{question}
"""

        response = model.generate_content(full_prompt)

        if response and response.text:
            return response.text

        return "I could not find a clear answer. Please try asking in a different way."

    except Exception as e:

        logger.error(f"Gemini API Error: {str(e)}")

        return "I'm having trouble connecting to my AI service. Please try again shortly."