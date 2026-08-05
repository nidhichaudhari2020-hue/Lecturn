from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_into_chunks(pages, chunk_size=500, chunk_overlap=100):
    """
    Split extracted PDF pages into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk in page_chunks:
            chunks.append({
                "page": page["page"],
                "text": chunk
            })

    return chunks