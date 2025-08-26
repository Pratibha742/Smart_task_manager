import os
from datetime import date

AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()

def ai_suggest_priority(text: str, due_date = None) -> str:
    """
    Classifies task urgency into Low, Medium, or High using:
    - Due date (highest priority check)
    - Gemini API (if AI_PROVIDER='gemini' and GEMINI_API_KEY set)
    - OpenAI API (if AI_PROVIDER='openai' and OPENAI_API_KEY set)
    - Keyword-based fallback logic (no API key required)
    """

       # ---------------- Due Date Logic ----------------
    if due_date:
        try:
            days_left = (due_date - date.today()).days
            if days_left <= 1:
                return "High"
            elif days_left <= 5:
                return "Medium"
            else:
                return "Low"
        except Exception as e:
            print(f"[DueDate Error] {e} — Falling back to AI/keywords.")

    # ---------------- Gemini ----------------
    if AI_PROVIDER == 'gemini' and os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            prompt = f"Classify the urgency of this task into Low, Medium, or High.\nTask: {text}\nReturn only the word."
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            out = response.text.strip().splitlines()[0].capitalize()
            return out if out in ('Low', 'Medium', 'High') else 'Medium'
        except Exception as e:
            print(f"[Gemini Error] {e} — Falling back to keyword logic.")

    # ---------------- OpenAI ----------------
    if AI_PROVIDER == 'openai' and os.getenv('OPENAI_API_KEY'):
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            prompt = f"Classify the urgency of this task into Low, Medium, or High.\nTask: {text}\nReturn only the word."
            resp = openai.Completion.create(
                model='text-davinci-003',
                prompt=prompt,
                max_tokens=3,
                temperature=0
            )
            out = resp.choices[0].text.strip().splitlines()[0].capitalize()
            return out if out in ('Low', 'Medium', 'High') else 'Medium'
        except Exception as e:
            print(f"[OpenAI Error] {e} — Falling back to keyword logic.")

    # ---------------- Fallback keyword logic ----------------
    text_lower = text.lower()
    if any(k in text_lower for k in ['urgent', 'asap', 'immediately', 'critical', 'now']):
        return 'High'
    if any(k in text_lower for k in ['soon', 'before', 'by', 'tomorrow']):
        return 'Medium'
    return 'Low'
