import pymupdf
import logging
from app.utils.progress import progress_bar

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        doc = pymupdf.open(pdf_path)  # open a document
        text = ""

        with progress_bar("Processing PDF pages...") as progress:
            task = progress.add_task("Processing PDF pages...", total=len(doc))

            for page in doc:  # iterate the document pages
                text += page.get_text()  # get plain text (is in UTF-8)
                progress.update(task, advance=1)

        return text
    except FileNotFoundError:
        error_msg = f"PDF file not found: {pdf_path}"
        logger.error(error_msg)
        raise
    except pymupdf.FileDataError:
        error_msg = f"Corrupted PDF file: {pdf_path}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error extracting text from PDF {pdf_path}: {str(e)}"
        logger.error(error_msg)
        raise
