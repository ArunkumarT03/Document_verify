# verify_docs.py
import google.generativeai as genai
import os

from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
def verify_document_text(doc_type, text):
    import json, re
    import google.generativeai as genai

    # Configure Gemini model
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={
            "temperature": 0.1,  # deterministic output
            "top_p": 1.0,
            "top_k": 1,
        }
    )

    prompt = f"""
You are a **financial document verification expert**.

The following text contains multiple salary slips and bank statements written in **Indonesian or English**.

 Your task:
1. Analyze all the documents carefully.
2. Decide whether they appear **genuine or fake** based ONLY on their **text content**.
3. Compare all salary slips with all bank statements — check for:
   - Consistent **employee names or IDs**
   - Consistent **company or organization names**
   - Matching or related **salary/credited amounts**
   - Consistent **months or payment dates**
4. Ignore completely:
   - Formatting, layout, structure, spelling, grammar, or design aspects.
   - Do NOT mark a document fake just because of appearance or typos.

Respond strictly in this JSON format (no markdown, no commentary):

{{
    "salary_slip_status": "Verified" or "Fake",
    "bank_statement_status": "Verified" or "Fake",
    "matched": "Matched" or "Not Matched",
    "explanation": "Explain logically in 3–5 sentences focusing only on names, company, month, and amount consistency between all documents."
}}

Documents Text:
{text}
"""


    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        cleaned_text = re.sub(r"```(?:json)?", "", result_text).replace("```", "").strip()
        result = json.loads(cleaned_text)
    except Exception:
        result = {
            "salary_slip_status": "Unknown",
            "bank_statement_status": "Unknown",
            "matched": "Unknown",
            "explanation": "Unable to parse model response."
        }

    return result
