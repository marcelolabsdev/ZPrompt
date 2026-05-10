import os
from openai import OpenAI
from services.templates import TEMPLATES

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        _client = OpenAI(api_key=api_key)
    return _client


async def generate_prompt(
    text: str,
    prompt_type: str,
    language: str | None = None,
    framework: str | None = None,
) -> str:
    template = TEMPLATES.get(prompt_type)
    if not template:
        raise ValueError(f"Tipo de prompt invalido: {prompt_type}")

    meta_prompt = template.format(user_input=text)

    if language or framework:
        context_parts = []
        if language:
            context_parts.append(f"Lenguaje principal: {language}")
        if framework:
            context_parts.append(f"Framework: {framework}")
        meta_prompt += "\n\nContexto adicional del usuario:\n" + "\n".join(
            context_parts
        )

    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Eres un experto en prompt engineering para desarrollo de software. Generas prompts precisos, estructurados y listos para usar. Siempre respondes en espanol.",
            },
            {"role": "user", "content": meta_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content
