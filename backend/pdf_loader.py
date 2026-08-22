import fitz  # PyMuPDF

def extract_text(pdf_path):
    """
    Extract text from PDF page by page.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    document.close()

    return pages
