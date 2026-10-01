import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.constants.current_affairs import AnalysisStatus, CurrentAffairCategory
from app.models.user import User
from app.models.current_affair import CurrentAffair
from app.models.question import InterviewQuestion
from app.models.resource import Resource
from app.models.document import Document, ProcessingStatus
from app.models.document_chunk import DocumentChunk, EmbeddingStatus
from app.services.current_affairs.base_source import BaseCurrentAffairsSource, CurrentAffairCandidate
from app.services.current_affairs.normalization_service import NormalizationService
from app.services.current_affairs.deduplication_service import DeduplicationService
from app.services.current_affairs.analysis_service import CurrentAffairsAnalysisService
from app.services.embedding_provider import get_embedding_provider

logger = logging.getLogger("current_affairs_ingestion")


class CurrentAffairsIngestionService:
    """Orchestrates ingestion, normalization, deduplication, Gemini analysis, question generation, and RAG indexing."""

    def __init__(
        self,
        db: Session,
        analysis_service: Optional[CurrentAffairsAnalysisService] = None,
        dedup_service: Optional[DeduplicationService] = None,
    ):
        self.db = db
        self.analysis_service = analysis_service or CurrentAffairsAnalysisService()
        self.dedup_service = dedup_service or DeduplicationService(db)

    def _get_or_create_system_user_id(self) -> str:
        existing_user = self.db.query(User).first()
        if existing_user:
            return existing_user.id
        
        system_user = User(
            email="system_ca@prashasak.ai",
            hashed_password="SystemPassword123!",
            full_name="Prashasak AI System",
            is_active=True,
        )
        self.db.add(system_user)
        self.db.commit()
        self.db.refresh(system_user)
        return system_user.id

    def process_candidate(
        self, candidate: CurrentAffairCandidate, auto_analyze: bool = True
    ) -> CurrentAffair:
        # 1. Normalize candidate
        norm_candidate = NormalizationService.normalize_candidate(candidate)

        # 2. Check duplicate
        duplicate = self.dedup_service.find_existing_duplicate(
            title=norm_candidate.title,
            source_url=norm_candidate.source_url,
        )
        if duplicate:
            logger.info(f"Duplicate current affair detected: '{norm_candidate.title}' -> matches ID {duplicate.id}")
            return duplicate

        # 3. Create CurrentAffair record
        slug = NormalizationService.generate_slug(norm_candidate.title)
        # Ensure slug uniqueness by appending timestamp if collision
        existing_slug = self.db.query(CurrentAffair).filter(CurrentAffair.slug == slug).first()
        if existing_slug:
            slug = f"{slug}-{int(datetime.now(timezone.utc).timestamp())}"

        current_affair = CurrentAffair(
            title=norm_candidate.title,
            slug=slug,
            summary=norm_candidate.summary or norm_candidate.content[:300],
            source_name=norm_candidate.source_name,
            source_url=norm_candidate.source_url,
            published_at=norm_candidate.published_at or datetime.now(timezone.utc),
            retrieved_at=datetime.now(timezone.utc),
            category=norm_candidate.category,
            topic=norm_candidate.topic,
            subtopic=norm_candidate.subtopic,
            content=norm_candidate.content,
            key_points=norm_candidate.key_points or [],
            analysis_status=AnalysisStatus.NORMALIZED.value,
        )

        self.db.add(current_affair)
        self.db.commit()
        self.db.refresh(current_affair)

        # 4. Analyze if enabled
        if auto_analyze and settings.CURRENT_AFFAIRS_ANALYSIS_ENABLED:
            self.analyze_and_publish(current_affair)

        return current_affair

    def analyze_and_publish(self, current_affair: CurrentAffair) -> CurrentAffair:
        """Trigger Gemini analysis, generate practice questions, and index into RAG vector search."""
        current_affair.analysis_status = AnalysisStatus.ANALYZING.value
        self.db.commit()

        try:
            analysis_result = self.analysis_service.analyze_item(
                title=current_affair.title,
                content=current_affair.content or current_affair.summary or "",
                source_name=current_affair.source_name,
                category=current_affair.category,
            )

            current_affair.summary = analysis_result.get("summary") or current_affair.summary
            current_affair.key_points = analysis_result.get("key_points") or current_affair.key_points or []
            current_affair.context = analysis_result.get("context")
            current_affair.policy_response = analysis_result.get("policy_response")
            current_affair.upsc_relevance = analysis_result.get("upsc_relevance")
            current_affair.interview_angle = analysis_result.get("interview_angle")
            if analysis_result.get("category"):
                current_affair.category = analysis_result["category"]
            if analysis_result.get("topic"):
                current_affair.topic = analysis_result["topic"]
            if analysis_result.get("subtopic"):
                current_affair.subtopic = analysis_result["subtopic"]

            current_affair.analysis_status = AnalysisStatus.ANALYZED.value
            self.db.commit()

            # 5. Generate Potential Practice Interview Questions
            self.generate_potential_questions(current_affair)

            # 6. Index into RAG Vector Knowledge Storage
            self.index_into_rag(current_affair)

            current_affair.analysis_status = AnalysisStatus.PUBLISHED.value
            self.db.commit()
            self.db.refresh(current_affair)
            return current_affair

        except Exception as e:
            logger.error(f"Failed to analyze current affair ID {current_affair.id}: {e}")
            self.db.rollback()
            current_affair.analysis_status = AnalysisStatus.FAILED.value
            self.db.commit()
            return current_affair

    def generate_potential_questions(self, current_affair: CurrentAffair) -> List[InterviewQuestion]:
        """Generate practice interview questions linked to the current affair."""
        # Clean existing generated questions for re-analysis
        self.db.query(InterviewQuestion).filter(
            InterviewQuestion.current_affair_id == current_affair.id
        ).delete(synchronize_session=False)

        questions: List[InterviewQuestion] = []
        topic_name = current_affair.topic or current_affair.title

        # 1. MAIN Question
        q_main = InterviewQuestion(
            current_affair_id=current_affair.id,
            question_text=f"How should India approach administrative and policy challenges arising from '{current_affair.title}'?",
            question_type="MAIN",
            difficulty="MODERATE",
            subject="Current Affairs",
            topic=topic_name,
            category=current_affair.category,
            explanation=current_affair.context or current_affair.summary,
            why_this_matters=current_affair.interview_angle or current_affair.upsc_relevance,
            status="ACTIVE",
        )
        questions.append(q_main)

        # 2. FOLLOW_UP Question
        q_followup = InterviewQuestion(
            current_affair_id=current_affair.id,
            question_text=f"What specific institutional or legal frameworks are relevant to implementing policy responses regarding '{topic_name}'?",
            question_type="FOLLOW_UP",
            difficulty="MODERATE",
            subject="Governance & Policy",
            topic=topic_name,
            category=current_affair.category,
            explanation=current_affair.policy_response or current_affair.context,
            why_this_matters="Tests understanding of administrative implementation machinery.",
            status="ACTIVE",
        )
        questions.append(q_followup)

        # 3. COUNTER Question
        q_counter = InterviewQuestion(
            current_affair_id=current_affair.id,
            question_text=f"Critics argue that interventions in '{topic_name}' might lead to unintended policy tradeoffs. How would you evaluate this viewpoint?",
            question_type="COUNTER",
            difficulty="CHALLENGING",
            subject="Policy Evaluation",
            topic=topic_name,
            category=current_affair.category,
            explanation=current_affair.interview_angle,
            why_this_matters="Evaluates ability to present balanced, objective arguments under pressure.",
            status="ACTIVE",
        )
        questions.append(q_counter)

        # 4. ETHICAL Question
        q_ethical = InterviewQuestion(
            current_affair_id=current_affair.id,
            question_text=f"What ethical responsibilities do civil servants have when balancing competing public interests in governance initiatives like '{topic_name}'?",
            question_type="ETHICAL",
            difficulty="CHALLENGING",
            subject="Ethics in Administration",
            topic=topic_name,
            category="ETHICS",
            explanation="Focuses on public interest, impartiality, and transparency.",
            why_this_matters="Evaluates ethical reasoning in administrative decision-making.",
            status="ACTIVE",
        )
        questions.append(q_ethical)

        # 5. SCENARIO Question
        q_scenario = InterviewQuestion(
            current_affair_id=current_affair.id,
            question_text=f"As a District Collector or Secretary, how would you design a stakeholder consultation process regarding '{topic_name}'?",
            question_type="SCENARIO",
            difficulty="MODERATE",
            subject="Administrative Leadership",
            topic=topic_name,
            category=current_affair.category,
            explanation=current_affair.policy_response or current_affair.summary,
            why_this_matters="Tests practical administrative problem-solving skills.",
            status="ACTIVE",
        )
        questions.append(q_scenario)

        for q in questions:
            self.db.add(q)

        self.db.commit()
        return questions

    def index_into_rag(self, current_affair: CurrentAffair) -> Optional[DocumentChunk]:
        """Indexes current affair into RAG Knowledge Base via Resource and DocumentChunk."""
        try:
            creator_user_id = self._get_or_create_system_user_id()
            resource_title = f"[Current Affair] {current_affair.title}"
            # Check if Resource already exists for this current affair
            resource = (
                self.db.query(Resource)
                .filter(Resource.title == resource_title)
                .first()
            )
            if not resource:
                resource = Resource(
                    title=resource_title,
                    description=current_affair.summary or current_affair.title,
                    resource_type="CURRENT_AFFAIRS",
                    category=current_affair.category,
                    subject="Current Affairs",
                    topic=current_affair.topic or "National Issues",
                    source=current_affair.source_name,
                    is_official=True,
                    created_by=creator_user_id,
                )
                self.db.add(resource)
                self.db.commit()
                self.db.refresh(resource)

            # Check Document
            doc = (
                self.db.query(Document)
                .filter(Document.resource_id == resource.id)
                .first()
            )
            if not doc:
                doc = Document(
                    resource_id=resource.id,
                    filename=f"current_affair_{current_affair.slug}.txt",
                    file_size=len(current_affair.content or ""),
                    processing_status=ProcessingStatus.COMPLETED.value,
                )
                self.db.add(doc)
                self.db.commit()
                self.db.refresh(doc)

            # Create chunk text
            chunk_content = (
                f"Title: {current_affair.title}\n"
                f"Source: {current_affair.source_name}\n"
                f"Category: {current_affair.category}\n"
                f"Topic: {current_affair.topic or ''}\n\n"
                f"Summary: {current_affair.summary or ''}\n\n"
                f"Key Points:\n" + "\n".join(f"- {kp}" for kp in (current_affair.key_points or [])) + "\n\n"
                f"Context: {current_affair.context or ''}\n\n"
                f"Policy Response: {current_affair.policy_response or ''}\n\n"
                f"UPSC Relevance: {current_affair.upsc_relevance or ''}\n\n"
                f"Interview Angle: {current_affair.interview_angle or ''}"
            )

            # Remove previous chunk if exists
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

            provider = get_embedding_provider()
            vector = provider.embed_text(chunk_content)

            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=0,
                page_number=1,
                content=chunk_content,
                chunk_metadata={
                    "current_affair_id": current_affair.id,
                    "title": current_affair.title,
                    "category": current_affair.category,
                    "topic": current_affair.topic,
                    "source_name": current_affair.source_name,
                    "source_url": current_affair.source_url,
                    "published_at": current_affair.published_at.isoformat() if current_affair.published_at else None,
                },
                embedding=vector,
                embedding_status=EmbeddingStatus.COMPLETED.value if vector else EmbeddingStatus.FAILED.value,
            )

            self.db.add(chunk)
            self.db.commit()
            return chunk

        except Exception as e:
            logger.error(f"Failed to index current affair ID {current_affair.id} into RAG: {e}")
            return None

    def ingest_source(
        self, source: BaseCurrentAffairsSource, limit: int = settings.CURRENT_AFFAIRS_FETCH_LIMIT
    ) -> List[CurrentAffair]:
        candidates = source.fetch_latest(limit=limit)
        results: List[CurrentAffair] = []
        for candidate in candidates:
            affair = self.process_candidate(candidate=candidate, auto_analyze=True)
            results.append(affair)
        return results
