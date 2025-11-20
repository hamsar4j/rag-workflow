"""Citation parser utility to extract sources from LLM responses."""

import re

from app.models.models import TextSegment


def parse_citations(text: str) -> list[TextSegment]:
    """
    Parse text with inline citations in the format [url] or [source: url] and return structured segments.
    Consecutive segments with the same source are automatically merged.

    Example input:
        "ASD is the Architecture pillar[https://example.com]. The ISTD tracks are AI[source: https://example2.com]."

    Example output:
        [
            TextSegment(text="ASD is the Architecture pillar", source="https://example.com"),
            TextSegment(text=". The ISTD tracks are AI", source="https://example2.com"),
            TextSegment(text=".", source=None)
        ]

    Args:
        text: The text with inline citations in square brackets (supports both [url] and [source: url] formats)

    Returns:
        List of TextSegment objects with text and optional source (merged when consecutive segments share the same source)
    """
    if not text:
        return [TextSegment(text="", source=None)]

    segments: list[TextSegment] = []

    # Pattern to match citations: [url] or [source: url]
    # This captures text before citation and the URL inside brackets
    pattern = r"(.*?)\[(?:source:\s*)?(https?://[^\]]+)\]"

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

    # Merge consecutive segments with the same source
    merged_segments: list[TextSegment] = []
    for segment in segments:
        if merged_segments and merged_segments[-1].source == segment.source:
            # Merge with previous segment if they have the same source
            merged_segments[-1] = TextSegment(
                text=merged_segments[-1].text + segment.text, source=segment.source
            )
        else:
            merged_segments.append(segment)

    return merged_segments
