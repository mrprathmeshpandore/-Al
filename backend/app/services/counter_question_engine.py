import re
import logging
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.question import InterviewQuestion
from app.models.interview import InterviewSessionQuestion, InterviewAnswer
from app.schemas.adaptive import CounterDecisionSchema
from app.services.gemini_service import get_gemini_service, BaseGeminiService
from app.services.question_validation_service import validate_generated_question

logger = logging.getLogger("counter_question_engine")

COUNTER_SYSTEM_INSTRUCTION = """
You are a senior UPSC Civil Services Interview Board Member evaluating a candidate's follow-up answer.

YOUR TASK:
Determine whether a COUNTER question is required to test whether the candidate can defend, qualify, or refine their position under constructive cross-examination.

CONSIDER A COUNTER QUESTION WHEN:
- The candidate takes a strong one-sided position without acknowledging trade-offs.
- Important stakeholder perspectives or constitutional/legal limitations are missing.
- Practical administrative or economic constraints are overlooked.
- Alternative defensible viewpoints exist that the candidate should address.

DO NOT GENERATE A COUNTER QUESTION WHEN:
- The candidate has already demonstrated well-balanced, nuanced reasoning.
- The candidate clearly qualified their position and acknowledged practical constraints.

STRICT JSON OUTPUT FORMAT:
{
  "should_counter": boolean,
  "reason": "Short operational note, e.g. Challenges one-sided position on policy",
  "counter_type": "COUNTER",
  "question": "Counter question text or null"
}
""".strip()


def normalize_text(text: str) -> str:
    clean = re.sub(r"[^\w\s]", "", (text or "").lower())
    return " ".join(clean.split())


class CounterQuestionEngine:
    """Service that evaluates follow-up responses and generates adaptive counter questions."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service or get_gemini_service()

    def evaluate_and_generate_counter(
        self,
        session_question: InterviewSessionQuestion,
        answer: InterviewAnswer,
        user: User,
    ) -> Tuple[bool, Optional[InterviewQuestion], Optional[str]]:
        """
        Evaluates a follow-up answer and generates a counter question if required.
        Returns: (should_counter, created_question_obj, reason_string)
        """
        parent_q = session_question.question
        q_text = parent_q.question_text if parent_q else "Follow-up Question"
        q_cat = parent_q.category if parent_q else "General"
        q_topic = parent_q.topic if parent_q else "Governance"

        # FAST-PATH PRE-SCREENING: Skip expensive Gemini network call if answer is blank or already scored exceptionally high (>= 8.5/10 or >= 85%)
        ans_text = (answer.answer_text or "").strip()
        words = ans_text.split()
        if len(words) < 2:
            logger.info("CounterQuestionEngine Fast-Path: Answer blank. Skipping counter question.")
            return False, None, "Response was empty; moving to next question."

        if answer.evaluation:
            e = answer.evaluation
            ov = e.overall_score or 0
            if ov >= 8.5 or ov >= 85:
                logger.info(f"CounterQuestionEngine Fast-Path: Candidate scored exceptional ({ov}). Skipping counter question.")
                return False, None, f"Response demonstrated balanced reasoning (Score: {ov})."

        # Evaluation context if available
        eval_context = ""
        if answer.evaluation:
            e = answer.evaluation
            eval_context = f"\nEVALUATION CONTEXT (Phase 10):\n- Balance Score: {e.balance_score}/10\n- Reasoning Score: {e.reasoning_score}/10\n- Feedback: {e.overall_feedback}"

        session_lang = session_question.session.language if (session_question and session_question.session and getattr(session_question.session, "language", None)) else "en-IN"
        target_lang_name = "English"
        if session_lang:
            clean_l = session_lang.lower()
            if "mr" in clean_l or "marathi" in clean_l:
                target_lang_name = "Marathi (मराठी)"
            elif "hi" in clean_l or "hindi" in clean_l:
                target_lang_name = "Hindi (हिंदी)"

        prompt = f"""
FOLLOW-UP QUESTION ASKED:
Text: {q_text}
Category: {q_cat}
Topic: {q_topic}

CANDIDATE ANSWER TO FOLLOW-UP:
{answer.answer_text}
(Duration: {answer.answer_duration_seconds}s)
{eval_context}

TARGET LANGUAGE: {target_lang_name}
CRITICAL LANGUAGE RULE: If a counter question is generated, output the question text strictly in {target_lang_name} (if Marathi or Hindi, write clean Devanagari script).

TASK:
Determine if a counter question is required. Output strict JSON only matching CounterDecisionSchema.
""".strip()

        try:
            raw_json = self.gemini_service.generate_json_response(
                prompt=prompt,
                system_instruction=COUNTER_SYSTEM_INSTRUCTION,
            )
            decision = CounterDecisionSchema(**raw_json)
        except Exception as ex:
            logger.warning(f"Failed to obtain/parse counter decision from Gemini: {ex}")
            return False, None, None

        if not decision.should_counter or not decision.question or not decision.question.strip():
            logger.info(f"CounterQuestionEngine: No counter question needed for session_question '{session_question.id}'.")
            return False, None, decision.reason

        q_str = decision.question.strip()

        # Validate duplicate against parent question
        if normalize_text(q_str) == normalize_text(q_text):
            logger.warning("Generated counter question is duplicate of parent question. Rejecting.")
            return False, None, None

        # Validate against existing questions in session
        existing_sqs = (
            self.db.query(InterviewSessionQuestion)
            .filter(InterviewSessionQuestion.session_id == session_question.session_id)
            .all()
        )
        for sq in existing_sqs:
            if sq.question and normalize_text(sq.question.question_text) == normalize_text(q_str):
                logger.warning("Generated counter question is duplicate of an existing session question. Rejecting.")
                return False, None, None

        # Validate using QuestionValidationService
        valid, err_msg = validate_generated_question({
            "question": q_str,
            "why_this_matters": "Adaptive counter question testing defence of position and balance.",
        })
        if not valid:
            logger.warning(f"Generated counter question failed validation: {err_msg}")
            return False, None, None

        # Persist InterviewQuestion record
        q_type = decision.counter_type if decision.counter_type in ["COUNTER", "ETHICAL", "SCENARIO"] else "COUNTER"
        counter_q = InterviewQuestion(
            question_text=q_str,
            question_type=q_type,
            difficulty=parent_q.difficulty if parent_q else "CHALLENGING",
            category=q_cat,
            topic=q_topic,
            is_personalized=parent_q.is_personalized if parent_q else False,
            personalization_source=parent_q.personalization_source if parent_q else None,
            personalization_label=parent_q.personalization_label if parent_q else None,
            explanation=f"Counter question challenging reasoning on: '{q_text[:60]}...'",
            why_this_matters="Tests candidate's resilience, balance, and ability to defend arguments under pressure.",
            user_id=user.id,
        )
        self.db.add(counter_q)
        self.db.commit()
        self.db.refresh(counter_q)

        logger.info(f"CounterQuestionEngine: Created counter question ID '{counter_q.id}'. Reason: {decision.reason}")
        return True, counter_q, decision.reason
