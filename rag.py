from typing import List, Any

from langchain_chroma import Chroma
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from app.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    TOP_K,
    validate_config,
)


class CustomerSupportRAG:
    """Retrieval-Augmented Generation engine for customer support."""

    def __init__(self):
        validate_config()

        # ============================================================
        # GEMINI EMBEDDINGS
        # ============================================================
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
        )

        # ============================================================
        # PERSISTENT CHROMADB
        # ============================================================
        self.vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=str(CHROMA_DIR),
        )

        # ============================================================
        # GEMINI CHAT MODEL
        # ============================================================
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )

        # ============================================================
        # RAG PROMPT
        # ============================================================
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI Customer Support Agent.

Your job is to answer customer questions using ONLY the
information provided in the retrieved knowledge base context.

Rules:
1. Be helpful, professional and concise.
2. Do not invent company policies, prices, refunds, delivery dates,
   contact information or product details.
3. If the answer cannot be found in the knowledge base, clearly say
   that the information is not available in the current knowledge base.
4. Do not pretend that you performed an action that you did not perform.
5. Use simple language that a customer can understand.

Retrieved Knowledge Base Context:
{context}
""",
                ),
                (
                    "human",
                    "{question}",
                ),
            ]
        )

    # ================================================================
    # RETRIEVAL
    # ================================================================
    def retrieve(self, question: str) -> List[Document]:
        """Retrieve the most relevant documents from ChromaDB."""

        return self.vectorstore.similarity_search(
            question,
            k=TOP_K,
        )

    # ================================================================
    # CONVERT GEMINI RESPONSE TO STRING
    # ================================================================
    def _extract_answer(self, content: Any) -> str:
        """
        Convert Gemini/LangChain response content into a plain string.

        Gemini may return content as:
            "plain text"

        or as:
            [{"type": "text", "text": "..."}]
        """

        # Normal string response
        if isinstance(content, str):
            return content.strip()

        # List of content blocks
        if isinstance(content, list):
            text_parts = []

            for item in content:
                # Dictionary content block
                if isinstance(item, dict):
                    text = item.get("text")

                    if text:
                        text_parts.append(str(text))

                # String content block
                elif isinstance(item, str):
                    text_parts.append(item)

            return "\n".join(text_parts).strip()

        # Fallback
        return str(content).strip()

    # ================================================================
    # ASK QUESTION
    # ================================================================
    def ask(self, question: str) -> dict:
        """Retrieve context and generate an answer."""

        # ------------------------------------------------------------
        # STEP 1: RETRIEVE RELEVANT DOCUMENTS
        # ------------------------------------------------------------
        documents = self.retrieve(question)

        if not documents:
            return {
                "answer": (
                    "I could not find relevant information in the "
                    "current knowledge base."
                ),
                "sources": [],
            }

        # ------------------------------------------------------------
        # STEP 2: BUILD KNOWLEDGE BASE CONTEXT
        # ------------------------------------------------------------
        context_parts = []

        for document in documents:
            source = document.metadata.get(
                "source",
                "Knowledge Base",
            )

            page = document.metadata.get("page")

            if page is not None:
                source_label = f"{source}, page {page + 1}"
            else:
                source_label = source

            context_parts.append(
                f"[Source: {source_label}]\n"
                f"{document.page_content}"
            )

        context = "\n\n".join(context_parts)

        # ------------------------------------------------------------
        # STEP 3: CREATE PROMPT
        # ------------------------------------------------------------
        messages = self.prompt.format_messages(
            context=context,
            question=question,
        )

        # ------------------------------------------------------------
        # STEP 4: ASK GEMINI
        # ------------------------------------------------------------
        response = self.llm.invoke(messages)

        # ------------------------------------------------------------
        # STEP 5: EXTRACT PLAIN TEXT FROM GEMINI RESPONSE
        # ------------------------------------------------------------
        answer = self._extract_answer(response.content)

        # Safety fallback
        if not answer:
            answer = (
                "I was unable to generate an answer from the "
                "current knowledge base."
            )

        # ------------------------------------------------------------
        # STEP 6: BUILD SOURCE INFORMATION
        # ------------------------------------------------------------
        sources = []

        for document in documents:
            source = document.metadata.get(
                "source",
                "Knowledge Base",
            )

            page = document.metadata.get("page")

            source_info = {
                "source": source,
            }

            if page is not None:
                source_info["page"] = page + 1

            # Avoid duplicate sources
            if source_info not in sources:
                sources.append(source_info)

        # ------------------------------------------------------------
        # STEP 7: RETURN FINAL RAG RESPONSE
        # ------------------------------------------------------------
        return {
            "answer": answer,
            "sources": sources,
        }


# ====================================================================
# GLOBAL RAG ENGINE
# ====================================================================

rag_engine = None


def get_rag_engine() -> CustomerSupportRAG:
    """Return a reusable RAG engine instance."""

    global rag_engine

    if rag_engine is None:
        rag_engine = CustomerSupportRAG()

    return rag_engine