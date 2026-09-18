from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import KNOWLEDGE_BASE_DIR, UPLOAD_DIR
from app.rag import get_rag_engine


# ============================================================
# AI CUSTOMER SUPPORT AGENT
# FastAPI Backend
# ============================================================

app = FastAPI(
    title="AI Customer Support Agent",
    description="RAG-based AI customer support system using Gemini, LangChain and ChromaDB.",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FRONTEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list


# ============================================================
# HOME
# ============================================================

@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(
        STATIC_DIR / "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "AI Customer Support Agent",
        "version": "1.0.0",
    }


# ============================================================
# CHAT
# ============================================================

@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        rag = get_rag_engine()

        result = rag.ask(question)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
        )

    except Exception as error:

        print(f"Chat error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question. Please check the server logs.",
        )


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/api/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    filename = Path(file.filename).name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    destination = UPLOAD_DIR / filename

    try:

        content = await file.read()

        destination.write_bytes(content)

        # Also copy into knowledge base
        knowledge_destination = KNOWLEDGE_BASE_DIR / filename

        knowledge_destination.write_bytes(content)

        return {
            "message": "PDF uploaded successfully.",
            "filename": filename,
            "location": str(knowledge_destination),
            "next_step": "Call /api/reindex to add the PDF to ChromaDB.",
        }

    except Exception as error:

        print(f"Upload error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Failed to upload PDF.",
        )


# ============================================================
# REINDEX KNOWLEDGE BASE
# ============================================================

@app.post("/api/reindex")
async def reindex():

    try:

        from app.ingest import (
            find_pdf_files,
            load_pdfs,
            split_documents,
            create_vector_database,
        )

        pdf_files = find_pdf_files()

        if not pdf_files:
            raise HTTPException(
                status_code=404,
                detail="No PDF files found in the knowledge base.",
            )

        documents = load_pdfs(pdf_files)

        chunks = split_documents(documents)

        create_vector_database(chunks)

        # Reset cached RAG engine so it reloads the database
        import app.rag as rag_module

        rag_module.rag_engine = None

        return {
            "message": "Knowledge base reindexed successfully.",
            "pdf_files": len(pdf_files),
            "pages": len(documents),
            "chunks": len(chunks),
        }

    except HTTPException:
        raise

    except Exception as error:

        print(f"Reindex error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Knowledge base reindexing failed.",
        )


# ============================================================
# RUN INFORMATION
# ============================================================

@app.get("/api/info")
async def project_info():

    return {
        "project": "AI Customer Support Agent",
        "architecture": "Retrieval-Augmented Generation",
        "backend": "FastAPI",
        "llm": "Google Gemini",
        "framework": "LangChain",
        "vector_database": "ChromaDB",
        "knowledge_base": "PDF",
    }
