import logging
from pathlib import Path
from typing import Union

import pymupdf

from app.utils.progress import progress_bar

logger = logging.getLogger(__name__)


def extract_text_from_pdf(
    pdf_source: Union[str, bytes, Path], source_name: str | None = None
) -> str:
    """Extract text from a PDF file path or raw bytes."""

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
        text = ""
        with progress_bar("Processing PDF pages...") as progress:
            task = progress.add_task("Processing PDF pages...", total=len(doc))
            for page in doc:
                text += page.get_text()
                progress.update(task, advance=1)

        return text
    finally:
        doc.close()
