from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    KNOWLEDGE_BASE_DIR,
    validate_config,
)


def find_pdf_files():
    """Find all PDF files inside the knowledge_base directory."""
    return list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))


def load_pdfs(pdf_files):
    """Load all PDF pages."""
    documents = []

    for pdf_file in pdf_files:
        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))
        pages = loader.load()

        for page in pages:
            page.metadata["source"] = pdf_file.name

        documents.extend(pages)

        print(f"  Loaded {len(pages)} page(s)")

    return documents


def split_documents(documents):
    """Split documents into smaller chunks for retrieval."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(documents)

    # Give every chunk an ID
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index

    return chunks


def create_vector_database(chunks):
    """Create/update the ChromaDB vector database."""

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )

    print("Creating ChromaDB vector database...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    return vectorstore


def main():
    print("=" * 60)
    print("AI CUSTOMER SUPPORT AGENT")
    print("Knowledge Base Ingestion")
    print("=" * 60)

    validate_config()

    pdf_files = find_pdf_files()

    if not pdf_files:
        print()
        print("No PDF files found.")
        print()
        print("Put your PDF files inside:")
        print(f"  {KNOWLEDGE_BASE_DIR}")
        print()
        print("Example:")
        print("  knowledge_base/customer_support.pdf")
        print()
        return

    print(f"\nFound {len(pdf_files)} PDF file(s).\n")

    documents = load_pdfs(pdf_files)

    print(f"\nTotal pages loaded: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    create_vector_database(chunks)

    print()
    print("=" * 60)
    print("KNOWLEDGE BASE READY")
    print("=" * 60)
    print(f"PDF files : {len(pdf_files)}")
    print(f"Pages     : {len(documents)}")
    print(f"Chunks    : {len(chunks)}")
    print(f"Database  : {CHROMA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
