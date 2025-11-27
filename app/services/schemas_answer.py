answer_schema = {
    "name": "final_answer_schema",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "JSON-encoded value. May represent a number, string, boolean, object, or base64 URI. Always returned as a string."
            },
            "post_url": {
                "type": "string",
                "description": "The URL where the final answer has been submitted."
            }
        },
        "required": ["answer"],
        "additionalProperties": False
    }
}
