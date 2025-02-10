from vertexai.generative_models import GenerationConfig, Part

with open("templates/bq_schema.md") as f:
    bq_schema = f.read()

system_instruction = f"""You are a BigQuery expert.
Please help to generate a BigQuery query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

=== Response Guidelines
1. If the provided context is sufficient, please generate a valid query without any explanations for the question. The query should start with a comment containing the question being asked.
2. If the provided context is insufficient, please explain why it can't be generated.
3. Please use the most relevant table(s).
4. Please format the query before responding.
5. Please always respond with a valid well-formed raw JSON object with the following format. WITHOUT code block marker.

=== Schema
{bq_schema}

Question: """

response_schema = {
    "type": "object",
    "description": "A couple of BigQuery query and explanation of failing reason.",
    "properties": {
        "query": {
            "type": "STRING",
            "description": "A generated BigQuery query will be described here when the context is sufficient.",
        },
        "explanation": {
            "type": "STRING",
            "description": "An explanation of failing to generate the query.",
        },
    },
    "required": ["query"],
}


txt2sql_conf = dict(
    model_name="gemini-1.5-flash",
    generation_config=GenerationConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        response_mime_type="application/json",
        response_schema=response_schema,
    ),
    system_instruction=[Part.from_text(system_instruction)],
)
