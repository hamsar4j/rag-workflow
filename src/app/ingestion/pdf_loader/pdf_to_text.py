import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        doc = pymupdf.open(pdf_path)  # open a document
        text = ""
        for page in doc:  # iterate the document pages
            text += page.get_text()  # get plain text (is in UTF-8)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return ""
