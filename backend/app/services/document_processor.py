import os
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.config import settings
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.services.pdf_extractor import extract_pdf_pages
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_pages
from app.services.embedding_service import process_chunk_embeddings

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

        # 5. Generate Batch Embeddings & Hashes via Embedding Service
        processed_chunks = process_chunk_embeddings(chunks_data)

        # Verify embedding success
        failed_count = sum(1 for c in processed_chunks if c.get("embedding_status") == EmbeddingStatus.FAILED.value)
        if failed_count > 0:
            document.processing_status = ProcessingStatus.FAILED.value
            document.page_count = page_count
            document.error_message = f"Embedding generation failed for {failed_count}/{len(processed_chunks)} chunks."
            document.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.error(f"Document {document_id} marked FAILED due to embedding errors.")
            return False

        # 6. Idempotent reprocessing: Delete old chunks for this document
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

        # 7. Bulk create DocumentChunks with embeddings and metadata
        new_chunk_objs = []
        for c in processed_chunks:
            chunk_obj = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                content=c["content"],
                content_hash=c.get("content_hash"),
                chunk_metadata=c.get("metadata"),
                embedding=c.get("embedding"),
                embedding_status=c.get("embedding_status", EmbeddingStatus.COMPLETED.value),
            )
            new_chunk_objs.append(chunk_obj)

        db.add_all(new_chunk_objs)

        # 8. Update Document Status to PROCESSED
        document.page_count = page_count
        document.processing_status = ProcessingStatus.PROCESSED.value
        document.error_message = None
        document.updated_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Document {document_id} successfully PROCESSED ({len(new_chunk_objs)} chunks, {page_count} pages).")
        return True

    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {e}")
        document.processing_status = ProcessingStatus.FAILED.value
        document.error_message = str(e)
        document.updated_at = datetime.now(timezone.utc)
        db.commit()
        return False
