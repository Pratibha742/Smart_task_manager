from datetime import date
import os

AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()

def ai_suggest_priority(text: str, due_date=None) -> str:
    """
    Hybrid priority logic:
    - AI suggestion based on task text
    - Due date urgency adjustment (always overrides if more urgent)
    """
    ai_priority = None
    due_priority = None

    # ---------------- AI Suggestion ----------------
    if AI_PROVIDER == 'gemini' and os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            prompt = f"Classify the urgency of this task into Low, Medium, or High.\nTask: {text}\nReturn only the word."
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            ai_priority = response.text.strip().splitlines()[0].capitalize()
        except Exception as e:
            print(f"[Gemini Error] {e} — Falling back to keyword logic.")

    elif AI_PROVIDER == 'openai' and os.getenv('OPENAI_API_KEY'):
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
            ai_priority = resp.choices[0].text.strip().splitlines()[0].capitalize()
        except Exception as e:
            print(f"[OpenAI Error] {e} — Falling back to keyword logic.")

    # ---------------- Keyword fallback ----------------
    if not ai_priority or ai_priority not in ('Low', 'Medium', 'High'):
        text_lower = text.lower()
        if any(k in text_lower for k in ['urgent', 'asap', 'immediately', 'critical', 'now']):
            ai_priority = 'High'
        elif any(k in text_lower for k in ['soon', 'before', 'by', 'tomorrow']):
            ai_priority = 'Medium'
        else:
            ai_priority = 'Low'

    # ---------------- Due Date Logic ----------------
    if due_date:
        try:
            days_left = (due_date - date.today()).days
            if days_left <= 2:
                due_priority = "High"
            elif 3 <= days_left <= 5:
                due_priority = "Medium"
            else:
                due_priority = "Low"
        except Exception as e:
            print(f"[DueDate Error] {e} — Skipping due_date adjustment.")

    # ---------------- Final Decision ----------------
    priority_levels = {"Low": 1, "Medium": 2, "High": 3}
    if due_priority:
        # pick whichever is more urgent
        return due_priority if priority_levels[due_priority] > priority_levels[ai_priority] else ai_priority
    return ai_priority


