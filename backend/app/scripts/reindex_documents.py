import sys
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.document import Document, ProcessingStatus
from app.services.document_processor import process_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reindex_documents")


def reindex_all_documents(force: bool = False, db: Optional[Session] = None):
    """
    CLI/Admin Service: Scans database for unprocessed/failed documents (or all if force=True) and re-runs processing.
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        query = db.query(Document)
        if not force:
            query = query.filter(
                or_(
                    Document.processing_status == ProcessingStatus.FAILED.value,
                    Document.processing_status == ProcessingStatus.UPLOADED.value,
                    Document.processing_status == ProcessingStatus.PROCESSING.value,
                )
            )

        documents = query.all()
        logger.info(f"Found {len(documents)} documents for re-indexing (force={force}).")

        success_count = 0
        failed_count = 0

        for doc in documents:
            logger.info(f"Re-indexing Document ID: {doc.id} ({doc.original_filename})...")
            result = process_document(doc.id, db)
            if result:
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"Re-indexing completed. Success: {success_count}, Failed: {failed_count}.")
        return {"success": success_count, "failed": failed_count}

    finally:
        if should_close_db:
            db.close()


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    reindex_all_documents(force=force_flag)
