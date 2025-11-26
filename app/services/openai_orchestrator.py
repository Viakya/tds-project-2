import json
import requests
from app.core.config import BASE_URL, MODEL, OPENAI_API_KEY

# Normalize URL
base = BASE_URL.rstrip("/")
if base.endswith("/v1"):
    base = base[:-3]
URL_CHAT = f"{base}/v1/chat/completions"

# -------- STRICT SCHEMA --------
collector_schema = {
    "name": "collector_schema",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "data_collection_script": {
                "type": "string",
                "description": "Python script that downloads ALL required external data."
            }
        },
        "required": ["data_collection_script"],
        "additionalProperties": False
    }
}

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}


async def generate_data_collection_script(html: str, quiz_url: str):
    prompt = f"""
You are a data extraction engine.

Your job:
1. READ the rendered HTML of a quiz page.
2. IDENTIFY all external datasets, URLs, APIs, or references.
3. CREATE a single Python script that:
   - downloads or scrapes ALL required data
   - saves each dataset (CSV/JSON/HTML) to local folder
   - uses ONLY: requests, pandas, bs4, lxml, json
4. NO browser automation. NO user input. NO credentials.
5. Script must be fully self-contained and runnable.

--- QUIZ URL ---
{quiz_url}

--- HTML CONTENT ---
{html}

Respond ONLY in STRICT JSON using the schema provided.
"""

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a data scraping engine."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": collector_schema
        }
    }

    # POST request
    resp = requests.post(URL_CHAT, headers=HEADERS, json=body, timeout=180)

    if resp.status_code != 200:
        raise Exception(f"OpenAI API error {resp.status_code}: {resp.text}")

    # Parse JSON response
    try:
        content = resp.json()["choices"][0]["message"]["content"]
        out = json.loads(content)
        return out["data_collection_script"]
    except Exception as e:
        raise Exception(f"JSON parse error: {e}\nRAW:\n{resp.text}")
