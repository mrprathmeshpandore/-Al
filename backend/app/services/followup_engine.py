import re
import logging
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSessionQuestion, InterviewAnswer
from app.schemas.adaptive import FollowupDecisionSchema
from app.services.gemini_service import get_gemini_service, BaseGeminiService
from app.services.question_validation_service import validate_generated_question

logger = logging.getLogger("followup_engine")

FOLLOWUP_SYSTEM_INSTRUCTION = """
You are a senior UPSC Civil Services Interview Board Member evaluating a practice response.

YOUR TASK:
Determine whether a FOLLOW_UP question is required based on the candidate's actual answer.

CONSIDER A FOLLOW-UP WHEN:
- The answer is incomplete or vague.
- The candidate makes an unsupported factual or policy claim.
- The candidate misses an important practical, constitutional, or economic trade-off.
- The candidate raises a key point worth probing further.

DO NOT GENERATE A FOLLOW-UP WHEN:
- The candidate's response is well-rounded, complete, and balanced.
- The answer already addresses core dimensions clearly.

STRICT JSON OUTPUT FORMAT:
{
  "should_follow_up": boolean,
  "reason": "Short operational note, e.g. Probes policy feasibility",
  "follow_up_type": "FOLLOW_UP",
  "question": "Follow-up question text or null"
}
""".strip()


def normalize_text(text: str) -> str:
    clean = re.sub(r"[^\w\s]", "", (text or "").lower())
    return " ".join(clean.split())


class FollowupEngine:
    """Service that evaluates candidate answers and generates adaptive follow-up questions."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service or get_gemini_service()

    def evaluate_and_generate_followup(
        self,
        session_question: InterviewSessionQuestion,
        answer: InterviewAnswer,
        user: User,
    ) -> Tuple[bool, Optional[InterviewQuestion], Optional[str]]:
        """
        Evaluates answer and generates a follow-up question if required.
        Returns: (should_follow_up, created_question_obj, reason_string)
        """
        parent_q = session_question.question
        q_text = parent_q.question_text if parent_q else "General UPSC Interview Question"
        q_cat = parent_q.category if parent_q else "General"
        q_topic = parent_q.topic if parent_q else "Governance"

        # Evaluation context if available
        eval_context = ""
        if answer.evaluation:
            e = answer.evaluation
            eval_context = f"\nEVALUATION CONTEXT (Phase 10):\n- Content Score: {e.content_score}/10\n- Depth Score: {e.depth_score}/10\n- Reasoning Score: {e.reasoning_score}/10\n- Balance Score: {e.balance_score}/10\n- Feedback: {e.overall_feedback}"

        prompt = f"""
ORIGINAL QUESTION:
Text: {q_text}
Category: {q_cat}
Topic: {q_topic}

CANDIDATE ANSWER:
{answer.answer_text}
(Duration: {answer.answer_duration_seconds}s)
{eval_context}

TASK:
Determine if a follow-up question is required. Output strict JSON only matching FollowupDecisionSchema.
""".strip()

        try:
            raw_json = self.gemini_service.generate_json_response(
                prompt=prompt,
                system_instruction=FOLLOWUP_SYSTEM_INSTRUCTION,
            )
            decision = FollowupDecisionSchema(**raw_json)
        except Exception as ex:
            logger.warning(f"Failed to obtain/parse follow-up decision from Gemini: {ex}")
            return False, None, None

        if not decision.should_follow_up or not decision.question or not decision.question.strip():
            logger.info(f"FollowupEngine: No follow-up needed for session_question '{session_question.id}'.")
            return False, None, decision.reason

        q_str = decision.question.strip()

        # Validate duplicate against parent question
        if normalize_text(q_str) == normalize_text(q_text):
            logger.warning("Generated follow-up is duplicate of parent question. Rejecting.")
            return False, None, None

        # Validate against existing questions in session
        existing_sqs = (
            self.db.query(InterviewSessionQuestion)
            .filter(InterviewSessionQuestion.session_id == session_question.session_id)
            .all()
        )
        for sq in existing_sqs:
            if sq.question and normalize_text(sq.question.question_text) == normalize_text(q_str):
                logger.warning("Generated follow-up is duplicate of an existing session question. Rejecting.")
                return False, None, None

        # Validate using QuestionValidationService
        valid, err_msg = validate_generated_question({
            "question": q_str,
            "why_this_matters": "Adaptive follow-up probing answer depth and reasoning.",
        })
        if not valid:
            logger.warning(f"Generated follow-up failed validation: {err_msg}")
            return False, None, None

        # Persist InterviewQuestion record
        q_type = decision.follow_up_type if decision.follow_up_type in ["FOLLOW_UP", "ETHICAL", "SCENARIO"] else "FOLLOW_UP"
        followup_q = InterviewQuestion(
            question_text=q_str,
            question_type=q_type,
            difficulty=parent_q.difficulty if parent_q else "MODERATE",
            category=q_cat,
            topic=q_topic,
            is_personalized=parent_q.is_personalized if parent_q else False,
            personalization_source=parent_q.personalization_source if parent_q else None,
            personalization_label=parent_q.personalization_label if parent_q else None,
            explanation=f"Follow-up question triggered by response to: '{q_text[:60]}...'",
            why_this_matters="Tests candidate's ability to elaborate on specific administrative or policy points.",
            user_id=user.id,
        )
        self.db.add(followup_q)
        self.db.commit()
        self.db.refresh(followup_q)

        logger.info(f"FollowupEngine: Created follow-up question ID '{followup_q.id}'. Reason: {decision.reason}")
        return True, followup_q, decision.reason
