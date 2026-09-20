import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.user import User
from app.models.resource import Resource
from app.models.document import Document, ProcessingStatus
from app.models.bookmark import ResourceBookmark
from app.schemas.resource import (
    ResourceResponse,
    ResourceUploadResponse,
    DocumentResponse,
    CategorySummary,
    SubjectSummary,
    BookmarkResponse,
)
from app.services.document_processor import process_document

router = APIRouter(prefix="/resources", tags=["Resources & PDF Knowledge Pipeline"])


def run_document_processing_job(document_id: str):
    """Background task wrapper creating an isolated DB session for async document processing."""
    db = SessionLocal()
    try:
        process_document(document_id, db)
    finally:
        db.close()


@router.post("/upload", response_model=ResourceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resource_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form("General Prep"),
    subject: str = Form("General Studies"),
    topic: Optional[str] = Form(None),
    resource_type: str = Form("pdf"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a PDF resource, validates MIME type and file size, saves to storage, and queues background processing.
    """
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files (application/pdf) are supported"
        )

    # Validate File Size
    file_content = await file.read()
    file_size = len(file_content)
    max_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_PDF_SIZE_MB}MB"
        )

    # Save File Safely
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex}.pdf"
    stored_path = os.path.join(settings.STORAGE_DIR, safe_filename)

    with open(stored_path, "wb") as f:
        f.write(file_content)

    # Create Resource Record
    resource = Resource(
        title=title.strip(),
        description=description.strip() if description else None,
        category=category.strip(),
        subject=subject.strip(),
        topic=topic.strip() if topic else None,
        resource_type=resource_type.strip(),
        is_official=False,
        created_by=current_user.id,
    )
    db.add(resource)
    db.flush()

    # Create Document Record
    document = Document(
        resource_id=resource.id,
        original_filename=filename,
        stored_filename=safe_filename,
        mime_type="application/pdf",
        file_size=file_size,
        page_count=0,
        processing_status=ProcessingStatus.UPLOADED.value,
        created_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(resource)
    db.refresh(document)

    # Trigger Async Document Processing in Background
    background_tasks.add_task(run_document_processing_job, document.id)

    return ResourceUploadResponse(
        resource_id=resource.id,
        document_id=document.id,
        processing_status=document.processing_status,
        message="PDF uploaded successfully. Processing document in background."
    )


@router.get("", response_model=List[ResourceResponse])
def list_resources(
    category: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lists all available study resources with optional category, subject, topic, and keyword search filters.
    """
    query = db.query(Resource)

    if category and category.lower() != "all":
        query = query.filter(Resource.category.ilike(f"%{category}%"))
    if subject:
        query = query.filter(Resource.subject.ilike(f"%{subject}%"))
    if topic:
        query = query.filter(Resource.topic.ilike(f"%{topic}%"))
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            Resource.title.ilike(search_term) |
            Resource.description.ilike(search_term) |
            Resource.subject.ilike(search_term)
        )

    resources = query.order_by(Resource.created_at.desc()).all()
    return resources


@router.get("/categories", response_model=List[CategorySummary])
def get_categories(db: Session = Depends(get_db)):
    """
    Returns categories with dynamic resource counts.
    """
    results = db.query(
        Resource.category,
        func.count(Resource.id).label("resource_count")
    ).group_by(Resource.category).all()

    return [CategorySummary(category=cat, resource_count=cnt) for cat, cnt in results]


@router.get("/subjects", response_model=List[SubjectSummary])
def get_subjects(db: Session = Depends(get_db)):
    """
    Returns subjects with dynamic resource counts for subject grids.
    """
    results = db.query(
        Resource.subject,
        func.count(Resource.id).label("resource_count")
    ).group_by(Resource.subject).all()

    return [SubjectSummary(subject=subj, resource_count=cnt) for subj, cnt in results]


@router.get("/bookmarked", response_model=List[ResourceResponse])
def get_bookmarked_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all resources bookmarked by the current authenticated user.
    """
    bookmarks = db.query(ResourceBookmark).filter(ResourceBookmark.user_id == current_user.id).all()
    resource_ids = [b.resource_id for b in bookmarks]

    if not resource_ids:
        return []

    resources = db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
    for r in resources:
        r.is_bookmarked = True
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource_detail(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns details for a single resource.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource


@router.get("/{resource_id}/documents", response_model=List[DocumentResponse])
def get_resource_documents(
    resource_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns linked document files and processing status for a resource.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    documents = db.query(Document).filter(Document.resource_id == resource_id).all()
    return documents


@router.post("/{resource_id}/bookmark", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bookmarks a resource for the authenticated user (prevents duplicates).
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    existing = db.query(ResourceBookmark).filter(
        ResourceBookmark.resource_id == resource_id,
        ResourceBookmark.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource is already bookmarked by this user"
        )

    bookmark = ResourceBookmark(
        resource_id=resource_id,
        user_id=current_user.id
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{resource_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Removes a bookmarked resource for the authenticated user.
    """
    bookmark = db.query(ResourceBookmark).filter(
        ResourceBookmark.resource_id == resource_id,
        ResourceBookmark.user_id == current_user.id
    ).first()

    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return None
