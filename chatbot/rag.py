from pathlib import Path
from typing import Iterable

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from pypdf import PdfReader
from qdrant_client import QdrantClient

from chatbot.config import get_settings


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 180) -> list[str]:
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def _read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _read_pdf_file(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"Page {page_number}\n{text}")
    return "\n\n".join(pages)


def _read_supported_file(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        return _read_pdf_file(file_path)
    return _read_text_file(file_path)


def _document_kind(file_path: Path) -> str:
    path_parts = {part.lower() for part in file_path.parts}
    if "docs" in path_parts:
        return "docs"
    return "personal_data"


def load_rag_documents(path: str | Path) -> list[Document]:
    source = Path(path)
    files: Iterable[Path]

    if source.is_dir():
        files = sorted(p for p in source.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS)
    elif source.is_file() and source.suffix.lower() in SUPPORTED_EXTENSIONS:
        files = [source]
    else:
        raise ValueError(f"Unsupported RAG path: {source}")

    docs: list[Document] = []
    for file_path in files:
        text = _read_supported_file(file_path)
        kind = _document_kind(file_path)
        for index, chunk in enumerate(_chunk_text(text)):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": str(file_path),
                        "chunk": index,
                        "kind": kind,
                        "file_type": file_path.suffix.lower().removeprefix("."),
                    },
                )
            )
    return docs


def load_personal_data_documents(path: str | Path) -> list[Document]:
    return load_rag_documents(path)


class PersonalDataRag:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.qdrant_url = self.settings.qdrant_url.rstrip("/")
        self.embeddings = FastEmbedEmbeddings(model_name=self.settings.embedding_model)
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.settings.qdrant_api_key or None,
            timeout=self.settings.qdrant_timeout,
        )

    def _store(self) -> QdrantVectorStore:
        return QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            collection_name=self.settings.qdrant_collection,
            url=self.qdrant_url,
            api_key=self.settings.qdrant_api_key or None,
            timeout=self.settings.qdrant_timeout,
        )

    def ingest_path(self, path: str | Path) -> int:
        docs = load_rag_documents(path)
        if not docs:
            return 0

        QdrantVectorStore.from_documents(
            documents=docs,
            embedding=self.embeddings,
            collection_name=self.settings.qdrant_collection,
            url=self.qdrant_url,
            api_key=self.settings.qdrant_api_key or None,
            timeout=self.settings.qdrant_timeout,
            force_recreate=False,
        )
        return len(docs)

    def search(self, query: str, k: int = 5) -> str:
        try:
            docs = self._store().similarity_search(query, k=k)
        except Exception as exc:
            return (
                "Personal data RAG is not ready. Ingest personal data first and confirm Qdrant is running. "
                f"Details: {exc}"
            )

        if not docs:
            return "No matching personal data memory found."

        formatted = []
        for idx, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            chunk = doc.metadata.get("chunk", "?")
            formatted.append(f"[{idx}] source={source} chunk={chunk}\n{doc.page_content}")
        return "\n\n".join(formatted)
