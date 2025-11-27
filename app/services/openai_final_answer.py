import json
import requests
from app.core.config import BASE_URL, MODEL, OPENAI_API_KEY
from app.services.schemas_answer import answer_schema

base = BASE_URL.rstrip("/")
if base.endswith("/v1"):
    base = base[:-3]
URL_CHAT = f"{base}/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

async def generate_final_answer(processor_stdout: str, html: str, quiz_url: str):
    prompt = f"""
You are an answer formatter for an autonomous data pipeline.

You receive:
- The quiz HTML
- The quiz URL
- The output printed by the data-processing script

Your job:
1. Understand from HTML & processing output whether the quiz expects a single value or multiple.
2. Find a URL where to POST the final answer , it is in the quiz url.
3. If ONE final value is expected, output EXACTLY that value as JSON field "answer".
4. If MULTIPLE outputs are expected, return an OBJECT nested inside "answer".
5. Allowed types for answer:
   - number
   - string
   - boolean
   - object (for multi-output)
6. DO NOT return arrays at top level.
7. Follow STRICT JSON schema.

--- QUIZ URL ---
{quiz_url}

--- HTML CONTENT ---
{html}

--- PROCESSOR OUTPUT ---
{processor_stdout}

Respond ONLY in strict JSON.
"""

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are the final answer formatter."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": answer_schema
        }
    }

    resp = requests.post(URL_CHAT, headers=HEADERS, json=body, timeout=180)

    if resp.status_code != 200:
        raise Exception(f"Final answer OpenAI error {resp.status_code}: {resp.text}")

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        out = json.loads(content)
        return out["answer"]

    except Exception as e:
        raise Exception(f"Final answer parse error: {e}\nRAW:\n{resp.text}")
