import logging
import random
import re
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSession, InterviewType, InterviewSessionQuestion
from app.services.question_generation_service import generate_interview_question
from app.services.personalization_service import generate_personalized_interview_question

from app.services.gemini_service import BaseGeminiService, get_gemini_service

logger = logging.getLogger("interview_orchestrator")

DYNAMIC_UPSC_TOPICS = [
    {"topic": "Public Administration & Governance", "category": "GOVERNANCE"},
    {"topic": "Ethics, Integrity & Administrative Discretion", "category": "ETHICS"},
    {"topic": "Socio-Economic Development & Agrarian Crisis", "category": "POLITY"},
    {"topic": "Constitutional Morality & Fundamental Rights", "category": "POLITY"},
    {"topic": "Internal Security & Disaster Management", "category": "SECURITY"},
    {"topic": "Environmental Governance & Climate Policy", "category": "ENVIRONMENT"},
    {"topic": "International Relations & Foreign Policy", "category": "INTERNATIONAL_RELATIONS"},
]


def normalize_q_text(text: Optional[str]) -> str:
    if not text:
        return ""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(clean.split())


class InterviewQuestionOrchestrator:
    """Orchestrates question selection/generation for an AI interview session reusing existing Phase 1–8 engines."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service or get_gemini_service()

    def get_or_create_next_question(
        self,
        session: InterviewSession,
        user: User,
        include_daf_questions: bool = True,
        include_current_affairs: bool = True,
        include_rag_questions: bool = True,
        difficulty: str = "MODERATE",
        topic: Optional[str] = None,
        category: Optional[str] = None,
    ) -> InterviewQuestion:
        # 1. Collect question_ids served in current session
        session_q_ids = [
            sq.question_id
            for sq in session.session_questions
            if sq.question_id is not None
        ]

        # 2. Collect past served questions (IDs and Normalized Texts) across all user history
        user_past_sqs = (
            self.db.query(InterviewSessionQuestion)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user.id)
            .all()
        )

        existing_q_ids = set(session_q_ids)
        existing_q_texts = set()

        for sq in user_past_sqs:
            if sq.question_id:
                existing_q_ids.add(sq.question_id)
            if sq.question:
                if sq.question.question_text:
                    existing_q_texts.add(normalize_q_text(sq.question.question_text))
                # If question was adapted from an original bank question, track the original parent ID & text
                if sq.question.personalization_label and "adapted_from:" in sq.question.personalization_label:
                    try:
                        parts = sq.question.personalization_label.split("adapted_from:")
                        for p in parts[1:]:
                            orig_id = p.split(":")[0].split("|")[0].strip()
                            if orig_id:
                                existing_q_ids.add(orig_id)
                                orig_q = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == orig_id).first()
                                if orig_q and orig_q.question_text:
                                    existing_q_texts.add(normalize_q_text(orig_q.question_text))
                    except Exception as err:
                        logger.debug(f"Error parsing adapted_from ID: {err}")

        existing_q_ids_list = list(existing_q_ids)

        # 1. DAF-Personalized Question Selection / Generation
        if session.interview_type == InterviewType.DAF_INTERVIEW.value or (
            include_daf_questions and (session.current_question_index % 2 == 1)
        ):
            daf_question = self._try_daf_question(
                user=user, difficulty=difficulty, existing_ids=existing_q_ids_list, existing_texts=existing_q_texts, language=session.language
            )
            if daf_question:
                return self._adapt_question_language(daf_question, session.language)

        # 2. Current Affairs Question Selection
        if session.interview_type == InterviewType.CURRENT_AFFAIRS.value or (
            include_current_affairs and (session.current_question_index % 3 == 0)
        ):
            ca_question = self._try_current_affairs_question(
                existing_ids=existing_q_ids_list, existing_texts=existing_q_texts, category=category
            )
            if ca_question:
                return self._adapt_question_language(ca_question, session.language)

        # 3. Existing Question Bank Match (Strictly text-deduplicated and randomized)
        bank_question = self._try_question_bank(
            existing_ids=existing_q_ids_list,
            existing_texts=existing_q_texts,
            user_id=user.id,
            difficulty=difficulty,
            category=category,
            topic=topic,
            language=session.language,
        )
        if bank_question:
            return self._adapt_question_language(bank_question, session.language)

        # 4. Fallback RAG-Grounded Dynamic AI Question Generation (UNLIMITED AI Questions)
        topics_to_try = list(DYNAMIC_UPSC_TOPICS)
        random.shuffle(topics_to_try)
        if topic:
            topics_to_try.insert(0, {"topic": topic, "category": category or "GOVERNANCE"})

        for t_info in topics_to_try[:3]:
            rag_question = self._try_rag_grounded_question(
                user=user,
                difficulty=difficulty,
                category=t_info.get("category") or "GOVERNANCE",
                topic=t_info.get("topic") or "Public Administration & Governance",
                language=session.language,
            )
            if rag_question and normalize_q_text(rag_question.question_text) not in existing_texts:
                return self._adapt_question_language(rag_question, session.language)

        # 5. Last Resort General UPSC Question (Randomized from active bank)
        fb_q = self._create_fallback_upsc_question(
            user=user, difficulty=difficulty, topic=topic, category=category, existing_ids=existing_q_ids_list, existing_texts=existing_q_texts, language=session.language
        )
        return self._adapt_question_language(fb_q, session.language)

    def _try_daf_question(
        self, user: User, difficulty: str, existing_ids: List[str], existing_texts: set, language: str = "en-IN"
    ) -> Optional[InterviewQuestion]:
        query = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.is_personalized.is_(True),
            or_(InterviewQuestion.user_id == user.id, InterviewQuestion.user_id.is_(None))
        )
        if existing_ids:
            query = query.filter(InterviewQuestion.id.notin_(existing_ids))
        
        candidates = query.order_by(func.random()).limit(50).all()
        for q in candidates:
            if normalize_q_text(q.question_text) not in existing_texts:
                return q

        sources = ["EDUCATION", "HOMETOWN", "OPTIONAL_SUBJECT", "HOBBY", "GENERAL_DAF"]
        src = random.choice(sources)
        try:
            res = generate_personalized_interview_question(
                db=self.db,
                current_user=user,
                source=src,
                difficulty=difficulty,
                language=language,
            )
            q_id = res.get("id")
            if q_id:
                q_obj = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
                if q_obj and normalize_q_text(q_obj.question_text) not in existing_texts:
                    return q_obj
        except Exception as e:
            logger.debug(f"DAF question generation skipped for source {src}: {e}")

        return None

    def _try_current_affairs_question(
        self, existing_ids: List[str], existing_texts: set, category: Optional[str]
    ) -> Optional[InterviewQuestion]:
        query = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.current_affair_id.isnot(None)
        )
        if category:
            query = query.filter(InterviewQuestion.category == category)
        if existing_ids:
            query = query.filter(InterviewQuestion.id.notin_(existing_ids))
        
        candidates = query.order_by(func.random()).limit(50).all()
        for q in candidates:
            if normalize_q_text(q.question_text) not in existing_texts:
                return q

        return None

    def _try_question_bank(
        self,
        existing_ids: List[str],
        existing_texts: set,
        user_id: str,
        difficulty: str,
        category: Optional[str],
        topic: Optional[str],
        language: str = "en-IN",
    ) -> Optional[InterviewQuestion]:
        clean_lang = (language or "en-IN").lower()
        is_target_devanagari = ("mr" in clean_lang or "marathi" in clean_lang or "hi" in clean_lang or "hindi" in clean_lang)

        # ULTRA-FAST MULTILINGUAL PASS: Search whole bank for unasked native/adapted Devanagari questions first
        if is_target_devanagari:
            dev_query = self.db.query(InterviewQuestion).filter(
                or_(
                    InterviewQuestion.user_id == user_id,
                    InterviewQuestion.user_id == "00000000-0000-0000-0000-000000000000",
                    InterviewQuestion.user_id.is_(None),
                )
            )
            if existing_ids:
                dev_query = dev_query.filter(InterviewQuestion.id.notin_(existing_ids))
            
            dev_candidates = dev_query.order_by(func.random()).limit(100).all()
            for q in dev_candidates:
                if normalize_q_text(q.question_text) not in existing_texts:
                    if re.search(r'[\u0900-\u097F]', q.question_text or "") or (q.personalization_label and "adapted_from:" in q.personalization_label):
                        return q

        query = self.db.query(InterviewQuestion).filter(
            or_(
                InterviewQuestion.user_id == user_id,
                InterviewQuestion.user_id == "00000000-0000-0000-0000-000000000000",
                InterviewQuestion.user_id.is_(None),
            )
        )
        if existing_ids:
            query = query.filter(InterviewQuestion.id.notin_(existing_ids))
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty == difficulty)
        if category:
            query = query.filter(InterviewQuestion.category == category)
        if topic:
            query = query.filter(InterviewQuestion.topic.ilike(f"%{topic}%"))

        candidates = query.order_by(func.random()).limit(50).all()

        is_target_english = ("en" in clean_lang or "english" in clean_lang)
        for q in candidates:
            if normalize_q_text(q.question_text) not in existing_texts:
                is_dev = bool(re.search(r'[\u0900-\u097F]', q.question_text or ""))
                if is_target_english and is_dev:
                    continue
                return q

        # Relax topic/difficulty filter
        relaxed_query = self.db.query(InterviewQuestion).filter(
            or_(
                InterviewQuestion.user_id == user_id,
                InterviewQuestion.user_id == "00000000-0000-0000-0000-000000000000",
                InterviewQuestion.user_id.is_(None),
            )
        )
        if existing_ids:
            relaxed_query = relaxed_query.filter(InterviewQuestion.id.notin_(existing_ids))
        
        relaxed_candidates = relaxed_query.order_by(func.random()).limit(100).all()
        if is_target_devanagari:
            for q in relaxed_candidates:
                if normalize_q_text(q.question_text) not in existing_texts:
                    if re.search(r'[\u0900-\u097F]', q.question_text or "") or (q.personalization_label and "adapted_from:" in q.personalization_label):
                        return q

        for q in relaxed_candidates:
            if normalize_q_text(q.question_text) not in existing_texts:
                is_dev = bool(re.search(r'[\u0900-\u097F]', q.question_text or ""))
                if is_target_english and is_dev:
                    continue
                return q

        return None

    def _try_rag_grounded_question(
        self, user: User, difficulty: str, category: str, topic: str, language: str = "en-IN"
    ) -> Optional[InterviewQuestion]:
        try:
            res = generate_interview_question(
                db=self.db,
                current_user_id=user.id,
                topic=topic,
                subject="General Studies",
                category=category,
                difficulty=difficulty,
                language=language,
            )
            q_id = res.get("id")
            if q_id:
                return self.db.query(InterviewQuestion).filter(InterviewQuestion.id == q_id).first()
        except Exception as e:
            logger.warning(f"RAG grounded question generation fallback error: {e}")
        return None

    def _create_fallback_upsc_question(
        self,
        user: User,
        difficulty: str,
        topic: Optional[str],
        category: Optional[str],
        existing_ids: List[str],
        existing_texts: set,
        language: str = "en-IN",
    ) -> InterviewQuestion:
        clean_lang = (language or "en-IN").lower()
        is_target_english = ("en" in clean_lang or "english" in clean_lang)

        # Try unasked active questions by text & ID matching requested language
        candidates = self.db.query(InterviewQuestion).filter(InterviewQuestion.status == "ACTIVE").order_by(func.random()).all()
        for q in candidates:
            if q.id not in existing_ids and normalize_q_text(q.question_text) not in existing_texts:
                is_dev = bool(re.search(r'[\u0900-\u097F]', q.question_text or ""))
                if is_target_english and is_dev:
                    continue
                return q

        # If all DB questions have been asked, dynamically generate a fresh RAG question
        try:
            random_topics = [
                "E-Governance & Digital Service Delivery",
                "District Administration & Disaster Preparedness",
                "Ethics in Public Service & Anti-Corruption Measures",
                "Fiscal Federalism & State Grants",
                "Agricultural Supply Chains & Farmer Welfare",
                "Urban Infrastructure & Smart City Missions",
                "Cyber Security & Critical Infrastructure Protection",
                "Judicial Reforms & Pendency of Cases",
                "Health Administration & Universal Health Coverage",
                "Renewable Energy & Sustainable Development",
            ]
            chosen_topic = random.choice(random_topics)
            rag_q = self._try_rag_grounded_question(
                user=user,
                difficulty=difficulty or "MODERATE",
                category=category or "GOVERNANCE",
                topic=chosen_topic,
            )
            if rag_q and normalize_q_text(rag_q.question_text) not in existing_texts:
                return rag_q
        except Exception as e:
            logger.warning(f"Fallback dynamic question generation error: {e}")

        # Emergency unique scenario generator
        import uuid
        unique_stamp = uuid.uuid4().hex[:6]
        default_q = InterviewQuestion(
            question_text=f"As a Civil Servant, how would you ensure administrative efficiency and transparency in policy implementation? (Scenario #{unique_stamp})",
            question_type="MAIN",
            difficulty=difficulty or "MODERATE",
            category=category or "GOVERNANCE",
            topic=topic or "Public Administration",
            user_id=user.id,
            status="ACTIVE",
        )
        self.db.add(default_q)
        self.db.commit()
        self.db.refresh(default_q)
        return default_q

    def _adapt_question_language(
        self, question: Optional[InterviewQuestion], target_language: Optional[str]
    ) -> Optional[InterviewQuestion]:
        """Adapts/translates question text and metadata into requested session language (Marathi/Hindi)."""
        if not question or not target_language:
            return question

        clean_lang = target_language.lower()
        if "en" in clean_lang or "english" in clean_lang:
            return question

        target_lang_name = "Marathi (मराठी)" if ("mr" in clean_lang or "marathi" in clean_lang) else "Hindi (हिंदी)"

        # Check if an adapted version of this question for this language already exists in DB
        adapted_tag = f"adapted_from:{question.id}:{clean_lang[:2]}"
        existing_adapted = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.personalization_label.like(f"%{adapted_tag}%")
        ).first()
        if existing_adapted:
            return existing_adapted

        try:
            prompt = (
                f"Translate and adapt this UPSC Interview Question into {target_lang_name}.\n\n"
                f"ORIGINAL QUESTION:\nText: {question.question_text}\nExplanation: {question.explanation or ''}\nWhy This Matters: {question.why_this_matters or ''}\n\n"
                f"STRICT INSTRUCTION: Output valid JSON with keys:\n"
                f"- \"question\": string (translated question in clean Devanagari script for {target_lang_name})\n"
                f"- \"explanation\": string (translated explanation)\n"
                f"- \"why_this_matters\": string (translated relevance)\n"
            )
            json_res = self.gemini_service.generate_json_response(
                prompt=prompt,
                system_instruction=f"You are a professional multilingual translator for UPSC Civil Services interviews. Translate strictly into {target_lang_name}."
            )
            new_text = json_res.get("question") or question.question_text
            new_exp = json_res.get("explanation") or question.explanation
            new_matters = json_res.get("why_this_matters") or question.why_this_matters

            new_label = f"{question.personalization_label}|{adapted_tag}" if question.personalization_label else adapted_tag

            # Return a new language-adapted question instance
            adapted_q = InterviewQuestion(
                question_text=new_text,
                question_type=question.question_type,
                difficulty=question.difficulty,
                category=question.category,
                topic=question.topic,
                is_personalized=question.is_personalized,
                personalization_source=question.personalization_source,
                personalization_label=new_label,
                explanation=new_exp,
                why_this_matters=new_matters,
                user_id=question.user_id,
            )
            self.db.add(adapted_q)
            self.db.commit()
            self.db.refresh(adapted_q)
            return adapted_q
        except Exception as e:
            logger.warning(f"Failed to adapt question to {target_language}: {e}")
            return question



