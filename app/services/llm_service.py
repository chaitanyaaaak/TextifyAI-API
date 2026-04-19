import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        logger.info(f"Initializing LLM client with model: {settings.LLM_MODEL}")
        _client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": settings.FRONTEND_URL,
                "X-Title": "TextifyAI",
            },
        )
    return _client


def safe_extract_content(response: Any) -> str:
    """Safely extract content from OpenAI response object."""
    try:
        if not response.choices:
            logger.warning("LLM response has no choices")
            return ""
        content = response.choices[0].message.content
        if content is None:
            logger.warning("LLM response choice has null content")
            return ""
        return content.strip()
    except (AttributeError, IndexError) as e:
        logger.error(f"Failed to extract content from LLM response: {e}")
        return ""


def safe_json_loads(text: str) -> Any:
    """
    Attempt to parse JSON from text, handling potential Markdown code blocks.
    Returns None if parsing fails.
    """
    if not text:
        return None
        
    text = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Try extracting from triple backticks
    import re
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    # Try finding the first '{' and last '}'
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
            
    return None


ROLE_SYSTEM_PROMPTS = {
    "lawyer": (
        "You are a legal writing assistant. You ONLY answer questions related to "
        "law, legal documents, contracts, briefs, court proceedings, and legal advice. "
        "Use structured professional Markdown for your responses. Use bolding for key terms, "
        "bullet points for lists, and headers for sections. "
        "If the user asks about anything outside the legal domain, refuse strictly and say: "
        "'I am specialized in the Legal field only. Please go back and choose your field carefully.'"
    ),
    "doctor": (
        "You are a medical writing assistant. You ONLY answer questions related to "
        "medicine, health, clinical notes, diagnoses, patient care, and medical documentation. "
        "Use structured anatomical and clinical Markdown for your responses. Use bullet points for "
        "symptoms/recommendations and bolding for critical medical terms. "
        "If the user asks about anything outside the medical domain, refuse strictly and say: "
        "'I am specialized in the Medical field only. Please go back and choose your field carefully.'"
    ),
    "engineer": (
        "You are a technical writing assistant. You ONLY answer questions related to "
        "engineering, technology, software, hardware, technical documentation, and specifications. "
        "Use structured technical Markdown. Use code blocks for snippets, bullet points for "
        "specifications, and headers for components. Avoid redundant bolding. "
        "If the user asks about anything outside the engineering/technical domain, refuse strictly and say: "
        "'I am specialized in the Engineering field only. Please go back and choose your field carefully.'"
    ),
    "faculty": (
        "You are an academic writing assistant. You ONLY answer questions related to "
        "academia, research papers, syllabi, grant proposals, teaching, and scholarly work. "
        "Use structured academic Markdown. Use blockquotes for citations and bullet points for "
        "abstracts or summaries. Maintain a formal tone. "
        "If the user asks about anything outside the academic domain, refuse strictly and say: "
        "'I am specialized in the Academic field only. Please go back and choose your field carefully.'"
    ),
    "writer": (
        "You are a creative writing assistant. You ONLY answer questions related to "
        "creative writing, storytelling, essays, prose, poetry, and narrative content. "
        "Use expressive but structured Markdown. Use italics for emphasis and dividers for "
        "scene breaks when appropriate. "
        "If the user asks about anything outside the creative writing domain, refuse strictly and say: "
        "'I am specialized in the Creative Writing field only. Please go back and choose your field carefully.'"
    ),
    "student": (
        "You are a student study assistant. You ONLY answer questions related to "
        "studying, assignments, essays, research papers, exam preparation, and academic learning. "
        "Use structured, easy-to-read Markdown. Use numbered lists for steps, bolding for "
        "definitions, and headers for topics to help with comprehension. "
        "If the user asks about anything outside academics, refuse strictly and say: "
        "'I am specialized in the Student/Academic field only. Please go back and choose your field carefully.'"
    ),
}


async def get_predictions(text: str, role: str, count: int = 5) -> list[str]:
    """Generate next-sentence predictions using OpenAI."""
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["student"])

    client = _get_client()
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": (
                f"{system_prompt}\n\n"
                f"The user is typing a sentence. Complete it in {count} different ways. "
                f"Return ONLY a JSON array of {count} strings, each being a full sentence "
                f"completion. No explanation, no markdown; just the JSON array."
            )},
            {"role": "user", "content": text},
        ],
        temperature=0.8,
        max_tokens=500,
    )

    raw = safe_extract_content(response)
    predictions = safe_json_loads(raw)
    if isinstance(predictions, list):
        return [str(p) for p in predictions[:count]]

    # Fallback: split by newlines if JSON parsing fails
    lines = [line.strip().strip("-•").strip() for line in raw.split("\n") if line.strip()]
    return lines[:count]


def _build_chat_messages(role: str, messages: list[dict]) -> list[dict]:
    """Convert frontend messages to OpenAI format with role system prompt."""
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["student"])
    openai_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        openai_role = "assistant" if msg["sender"] == "assistant" else "user"
        openai_messages.append({"role": openai_role, "content": msg["text"]})

    return openai_messages


async def get_chat_reply(role: str, messages: list[dict]) -> str:
    """Get a single chat reply from OpenAI."""
    client = _get_client()
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=_build_chat_messages(role, messages),
        temperature=0.7,
        max_tokens=1024,
    )
    return safe_extract_content(response)


async def stream_chat_reply(role: str, messages: list[dict]):
    """Yield chat tokens one by one from OpenAI streaming."""
    client = _get_client()
    stream = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=_build_chat_messages(role, messages),
        temperature=0.7,
        max_tokens=1024,
        stream=True,
    )

    async for chunk in stream:
        try:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
        except (AttributeError, IndexError):
            continue


async def get_structured_chat_reply(role: str, messages: list[dict]) -> dict:
    """
    Get a chat reply. For casual messages returns a simple reply; for
    informational queries returns a description + numbered points.

    Returns one of:
      {"type": "chat", "text": "..."}
      {"type": "structured", "description": "...", "points": ["...", ...]}
    """
    base_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["student"])
    structured_prompt = (
        f"{base_prompt}\n\n"
        "You must always respond with valid json. "
        "Decide the format based on the user's message:\n"
        "- Casual (greetings, thanks, small talk) → return json:\n"
        '  {"type": "chat", "text": "<your reply>"}\n'
        "- Informational question → return json:\n"
        '  {"type": "structured", "description": "<one sentence overview, max 20 words>", '
        '"points": ["<point 1, max 15 words>", "<point 2>", "<point 3>"]}\n'
        "Return 3 to 5 points for structured replies. No markdown, no extra keys."
    )

    chat_messages = [{"role": "system", "content": structured_prompt}]
    for msg in messages:
        openai_role = "assistant" if msg["sender"] == "assistant" else "user"
        chat_messages.append({"role": openai_role, "content": msg["text"]})

    client = _get_client()
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=chat_messages,
        temperature=0.7,
        max_tokens=512,
        response_format={"type": "json_object"},
    )

    raw = safe_extract_content(response)
    result = safe_json_loads(raw)
    if result and isinstance(result, dict):
        if result.get("type") in ("chat", "structured"):
            return result

    # Fallback: treat as casual reply
    return {"type": "chat", "text": raw[:200] if raw else "Unexpected AI response format."}
