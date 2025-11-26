answer_schema = {
    "name": "final_answer_schema",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "answer": {
                "oneOf": [
                    {"type": "number"},
                    {"type": "string"},
                    {"type": "boolean"},
                    {
                        "type": "object",
                        "additionalProperties": True
                    }
                ]
            }
        },
        "required": ["answer"],
        "additionalProperties": False
    }
}
