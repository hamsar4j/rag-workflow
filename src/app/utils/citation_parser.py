"""Citation parser utility to extract sources from LLM responses."""

import re
from app.models.models import TextSegment


def parse_citations(text: str) -> list[TextSegment]:
    """
    Parse text with inline citations in the format [url] and return structured segments.

    Example input:
        "ASD is the Architecture pillar[https://example.com]. The ISTD tracks are AI[https://example2.com]."

    Example output:
        [
            TextSegment(text="ASD is the Architecture pillar", source="https://example.com"),
            TextSegment(text=". The ISTD tracks are AI", source="https://example2.com"),
            TextSegment(text=".", source=None)
        ]

    Args:
        text: The text with inline citations in square brackets

    Returns:
        List of TextSegment objects with text and optional source
    """
    if not text:
        return [TextSegment(text="", source=None)]

    segments: list[TextSegment] = []

    # Pattern to match citations: [url]
    # This captures text before citation and the URL inside brackets
    pattern = r"(.*?)\[(https?://[^\]]+)\]"

    last_end = 0

    for match in re.finditer(pattern, text):
        text_before = match.group(1)
        url = match.group(2)

        if text_before:
            segments.append(TextSegment(text=text_before, source=url))

        last_end = match.end()

    # Add any remaining text after the last citation
    remaining = text[last_end:]
    if remaining:
        segments.append(TextSegment(text=remaining, source=None))

    # If no citations were found, return the whole text as one segment
    if not segments:
        segments.append(TextSegment(text=text, source=None))

    return segments
