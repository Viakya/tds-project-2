import json
import requests
from app.core.config import BASE_URL, MODEL, OPENAI_API_KEY

# Normalize BASE_URL (same as collector)
base = BASE_URL.rstrip("/")
if base.endswith("/v1"):
    base = base[:-3]
URL_CHAT = f"{base}/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

processing_schema = {
    "name": "processing_schema",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "data_processing_script": {
                "type": "string",
                "description": "Python script that processes scraped data into the final answer."
            }
        },
        "required": ["data_processing_script"],
        "additionalProperties": False
    }
}

async def generate_data_processing_script(html: str, quiz_url: str, scraped_file_list: list):
    prompt = f"""
You are a data processing engine for an autonomous pipeline.

INPUTS YOU HAVE:
1. Rendered HTML of a quiz page
2. The quiz URL
3. A list of scraped files from the previous step

Task:
- Analyze the HTML and understand what the question is asking.
- Look at the scraped file names and infer which contain the useful data.
- Produce a Python script that:
    - loads these scraped files
    - processes/filters/merges them
    - computes the exact answer required by the quiz
    - writes processed output into the working directory
    - prints the answer clearly

Rules:
- Use ONLY pandas, numpy, json, bs4, lxml
- NO system calls, NO external network requests
- Must be fully runnable in isolation
- Must NOT require human input
- File paths must be relative, assuming the script runs inside the folder containing the scraped files.

--- QUIZ URL ---
{quiz_url}

--- HTML CONTENT ---
{html}

--- SCRAPED FILES ---
{json.dumps(scraped_file_list, indent=2)}

Respond ONLY using the strict JSON schema.
"""

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a data processing engine."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": processing_schema
        }
    }

    resp = requests.post(URL_CHAT, headers=HEADERS, json=body, timeout=180)

    if resp.status_code != 200:
        raise Exception(f"Processing OpenAI API error {resp.status_code}: {resp.text}")

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        out = json.loads(content)
        return out["data_processing_script"]
    except Exception as e:
        raise Exception(f"Processing JSON parse error: {e}\nRAW:\n{resp.text}")
