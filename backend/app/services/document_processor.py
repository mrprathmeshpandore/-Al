import os
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.config import settings
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk
from app.services.pdf_extractor import extract_pdf_pages
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_pages
from app.services.embedding_provider import get_embedding_provider

logger = logging.getLogger("document_processor")


def process_document(document_id: str, db: Session) -> bool:
    """
    Executes the PDF Document Processing Pipeline:
    Uploaded PDF -> Validate -> Extract Pages -> Clean -> Chunk -> Embed -> Database Persistence -> Status Update.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        logger.error(f"Document ID {document_id} not found for processing.")
        return False

    try:
        # 1. Update status to PROCESSING
        document.processing_status = ProcessingStatus.PROCESSING.value
        document.updated_at = datetime.now(timezone.utc)
        db.commit()

        file_path = os.path.join(settings.STORAGE_DIR, document.stored_filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Stored document file not found at {file_path}")

        # 2. Extract PDF Pages
        extracted = extract_pdf_pages(file_path)
        page_count = extracted["page_count"]
        raw_pages = extracted["pages"]

        # 3. Clean Text Page-by-Page
        cleaned_pages = []
        total_text_length = 0
        for p in raw_pages:
            ct = clean_text(p["text"])
            total_text_length += len(ct)
            cleaned_pages.append({
                "page_number": p["page_number"],
                "text": ct
            })

        # Check if PDF has extractable text
        if total_text_length == 0:
            document.processing_status = ProcessingStatus.FAILED.value
            document.page_count = page_count
            document.error_message = "No extractable text found in PDF (scanned or image-only PDF)."
            document.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.warning(f"Document {document_id} marked FAILED due to empty extractable text.")
            return False

        # 4. Chunk Pages
        chunks_data = chunk_pages(cleaned_pages, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

        if not chunks_data:
            document.processing_status = ProcessingStatus.FAILED.value
            document.page_count = page_count
            document.error_message = "Document text could not be chunked into valid text blocks."
            document.updated_at = datetime.now(timezone.utc)
            db.commit()
            return False

        # 5. Generate Embeddings
        embedding_provider = get_embedding_provider()
        chunk_contents = [c["content"] for c in chunks_data]
        embeddings = embedding_provider.embed_documents(chunk_contents)

        # 6. Delete old chunks if any
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

        # 7. Bulk create DocumentChunks
        new_chunks = []
        for i, c in enumerate(chunks_data):
            emb = embeddings[i] if i < len(embeddings) else None
            chunk_obj = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                content=c["content"],
                chunk_metadata=c["metadata"],
                embedding=emb,
            )
            new_chunks.append(chunk_obj)

        db.add_all(new_chunks)

        # 8. Update Document Status to PROCESSED
        document.page_count = page_count
        document.processing_status = ProcessingStatus.PROCESSED.value
        document.error_message = None
        document.updated_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Document {document_id} successfully PROCESSED ({len(new_chunks)} chunks, {page_count} pages).")
        return True

    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {e}")
        document.processing_status = ProcessingStatus.FAILED.value
        document.error_message = str(e)
        document.updated_at = datetime.now(timezone.utc)
        db.commit()
        return False
