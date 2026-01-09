import logging
from pathlib import Path
from typing import Union

import pymupdf
import pymupdf4llm

logger = logging.getLogger(__name__)


def extract_text_from_pdf(
    pdf_source: Union[str, bytes, Path], source_name: str | None = None
) -> str:
    """Extract text from a PDF file path or raw bytes as markdown."""

    source_label = source_name or (
        str(pdf_source) if isinstance(pdf_source, (str, Path)) else "uploaded-pdf"
    )

    try:
        if isinstance(pdf_source, (str, Path)):
            doc = pymupdf.open(pdf_source)
        else:
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
    except FileNotFoundError:
        error_msg = f"PDF file not found: {source_label}"
        logger.error(error_msg)
        raise
    except pymupdf.FileDataError:
        error_msg = f"Corrupted PDF file: {source_label}"
        logger.error(error_msg)
        raise
    except Exception as exc:
        error_msg = f"Error opening PDF {source_label}: {exc}"
        logger.error(error_msg)
        raise

    try:
        markdown_text = pymupdf4llm.to_markdown(doc, show_progress=True)
        return markdown_text
    finally:
        doc.close()
