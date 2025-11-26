import requests

def submit_answer(email: str, secret: str, url: str, answer):
    payload = {
        "email": email,
        "secret": secret,
        "url": url,
        "answer": answer
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        return {
            "status_code": resp.status_code,
            "response": resp.text
        }
    except Exception as e:
        return {
            "status_code": None,
            "response": str(e)
        }
