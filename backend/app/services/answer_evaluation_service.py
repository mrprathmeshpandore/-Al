import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.interview import InterviewAnswer, InterviewSessionQuestion, InterviewSession
from app.models.evaluation import InterviewAnswerEvaluation
from app.schemas.evaluation import EvaluationResult, EvaluationDimension
from app.services.gemini_service import get_gemini_service, BaseGeminiService

logger = logging.getLogger("answer_evaluation_service")

# Configurable Dimension Weights
DIMENSION_WEIGHTS = {
    "content": 0.20,
    "clarity": 0.15,
    "depth": 0.20,
    "reasoning": 0.20,
    "balance": 0.15,
    "communication": 0.10,
}

SYSTEM_EVALUATION_INSTRUCTION = """
You are a senior UPSC Civil Services Personality Test (Interview) Panel Member evaluating a candidate's response.

EVALUATION BENCHMARKS & SCORING GUIDELINES:
- EXCELLENT (8.0 - 10.0): The response directly addresses the question with sound administrative reasoning, stakeholder perspective, constitutional balance, and constructive policy solutions (e.g., balancing development with public trust, compensation, dialogue, and legal frameworks).
- GOOD (6.0 - 7.9): The response covers relevant points and shows logical thinking, but could include deeper policy context or structured presentation.
- NEEDS WORK (0.0 - 5.9): The response is off-topic, extremely brief (e.g., only 1-3 words), or lacks basic administrative awareness.

IMPORTANT RULES:
- DO NOT BE OVERLY HARSH: When a candidate provides a structured, multi-faceted administrative answer (such as balancing infrastructure development with farmer welfare, dialogue, compensation, and trust), award HIGH scores (8.0 to 9.5).
- IGNORE CASING & STT ARTIFACTS: Do not penalize capitalization, title casing, or minor speech-to-text transcript quirks. Focus strictly on core concepts, analytical depth, and administrative reasoning.
- LANGUAGE FLEXIBILITY: The candidate may answer in English, Marathi, or a mix of both. Evaluate the core meaning accurately and provide your feedback in the primary language used by the candidate.
- Output MUST strictly be valid JSON matching the requested schema without extra text or markdown formatting.
""".strip()


def calculate_authoritative_overall_score(result: EvaluationResult) -> float:
    """Calculates authoritative overall weighted score on backend normalized between 0.0 and 10.0."""
    total = (
        result.content.score * DIMENSION_WEIGHTS["content"]
        + result.clarity.score * DIMENSION_WEIGHTS["clarity"]
        + result.depth.score * DIMENSION_WEIGHTS["depth"]
        + result.reasoning.score * DIMENSION_WEIGHTS["reasoning"]
        + result.balance.score * DIMENSION_WEIGHTS["balance"]
        + result.communication.score * DIMENSION_WEIGHTS["communication"]
    )
    return round(max(0.0, min(10.0, total)), 2)


class AnswerEvaluationService:
    """Service handling AI answer evaluation, backend score calculation, persistence, and retrieval."""

    def __init__(self, db: Session, gemini_service: Optional[BaseGeminiService] = None):
        self.db = db
        self.gemini_service = gemini_service or get_gemini_service()

    def evaluate_answer(self, answer_id: str, user_id: str) -> InterviewAnswerEvaluation:
        """
        Evaluates a candidate answer.
        IDEMPOTENCY: Returns existing evaluation if answer was already evaluated.
        """
        answer = (
            self.db.query(InterviewAnswer)
            .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewAnswer.id == answer_id, InterviewSession.user_id == user_id)
            .first()
        )

        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview answer not found or access denied.",
            )

        # IDEMPOTENCY CHECK: Return existing evaluation if present
        if answer.evaluation:
            logger.info(f"Evaluation for answer '{answer_id}' already exists. Returning stored evaluation.")
            return answer.evaluation

        sq = answer.session_question
        question = sq.question

        q_text = question.question_text if question else "General UPSC Interview Question"
        q_type = question.question_type if question else "MAIN"
        q_diff = question.difficulty if question else "MODERATE"
        q_cat = question.category if question else "General"
        q_topic = question.topic if question else "Governance"

        session_lang = sq.session.language if (sq and sq.session and getattr(sq.session, "language", None)) else "en-IN"
        target_lang_name = "English"
        if session_lang:
            clean_l = session_lang.lower()
            if "mr" in clean_l or "marathi" in clean_l:
                target_lang_name = "Marathi (मराठी)"
            elif "hi" in clean_l or "hindi" in clean_l:
                target_lang_name = "Hindi (हिंदी)"

        prompt = f"""
INTERVIEW QUESTION:
Text: {q_text}
Type: {q_type}
Difficulty: {q_diff}
Category: {q_cat}
Topic: {q_topic}

CANDIDATE ANSWER:
Answer Text: {answer.answer_text}
Duration: {answer.answer_duration_seconds} seconds

TARGET FEEDBACK LANGUAGE: {target_lang_name}

CRITICAL LANGUAGE RULE: Evaluate the candidate's answer thoroughly. Write all textual feedback, feedback sentences, overall_feedback, strengths, areas_to_improve, and suggested_answer strictly in {target_lang_name} (if Marathi or Hindi, write clean Devanagari script).

TASK:
Provide a structured evaluation in JSON format containing:
- content: {{ "score": float (0-10), "feedback": string }}
- clarity: {{ "score": float (0-10), "feedback": string }}
- depth: {{ "score": float (0-10), "feedback": string }}
- reasoning: {{ "score": float (0-10), "feedback": string }}
- balance: {{ "score": float (0-10), "feedback": string }}
- communication: {{ "score": float (0-10), "feedback": string }}
- overall_feedback: string summary
- strengths: list of short strings
- areas_to_improve: list of short strings
- suggested_answer: comprehensive structured model response text
""".strip()

        logger.info(f"Requesting AI evaluation for answer_id '{answer_id}'...")

        try:
            raw_json = self.gemini_service.generate_json_response(
                prompt=prompt,
                system_instruction=SYSTEM_EVALUATION_INSTRUCTION,
            )
        except Exception as e:
            logger.error(f"Gemini service failure for answer '{answer_id}': {e}. Using deterministic fallback.")
            from app.services.gemini_service import FakeGeminiService
            fallback_service = FakeGeminiService()
            raw_json = fallback_service.generate_json_response(
                prompt=prompt,
                system_instruction=SYSTEM_EVALUATION_INSTRUCTION,
            )

        # Validate structured output using Pydantic
        try:
            validated_result = EvaluationResult(**raw_json)
        except ValidationError as ve:
            logger.error(f"Invalid evaluation JSON output for answer '{answer_id}': {ve}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"AI evaluation provider returned invalid evaluation structure: {ve}",
            )
        except Exception as ex:
            logger.error(f"Unexpected parsing error for answer '{answer_id}': {ex}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AI evaluation output could not be parsed.",
            )

        # Calculate authoritative overall score on backend
        authoritative_score = calculate_authoritative_overall_score(validated_result)

        # Store evaluation in DB
        evaluation = InterviewAnswerEvaluation(
            answer_id=answer.id,
            content_score=validated_result.content.score,
            content_feedback=validated_result.content.feedback,
            clarity_score=validated_result.clarity.score,
            clarity_feedback=validated_result.clarity.feedback,
            depth_score=validated_result.depth.score,
            depth_feedback=validated_result.depth.feedback,
            reasoning_score=validated_result.reasoning.score,
            reasoning_feedback=validated_result.reasoning.feedback,
            balance_score=validated_result.balance.score,
            balance_feedback=validated_result.balance.feedback,
            communication_score=validated_result.communication.score,
            communication_feedback=validated_result.communication.feedback,
            overall_score=authoritative_score,
            overall_feedback=validated_result.overall_feedback,
            strengths=validated_result.strengths,
            areas_to_improve=validated_result.areas_to_improve,
            suggested_answer=validated_result.suggested_answer,
        )

        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        logger.info(f"Successfully evaluated answer_id '{answer_id}' with overall score {authoritative_score}.")
        return evaluation

    def get_evaluation(self, answer_id: str, user_id: str) -> InterviewAnswerEvaluation:
        """Retrieves existing answer evaluation for the authenticated user."""
        answer = (
            self.db.query(InterviewAnswer)
            .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .join(InterviewSession, InterviewSessionQuestion.session_id == InterviewSession.id)
            .filter(InterviewAnswer.id == answer_id, InterviewSession.user_id == user_id)
            .first()
        )

        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview answer not found or access denied.",
            )

        if not answer.evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation does not exist for this answer.",
            )

        return answer.evaluation

    def get_session_evaluations(self, session_id: str, user_id: str) -> List[InterviewAnswerEvaluation]:
        """Retrieves all answer evaluations belonging to a session."""
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied.",
            )

        evaluations = (
            self.db.query(InterviewAnswerEvaluation)
            .join(InterviewAnswer, InterviewAnswerEvaluation.answer_id == InterviewAnswer.id)
            .join(InterviewSessionQuestion, InterviewAnswer.session_question_id == InterviewSessionQuestion.id)
            .filter(InterviewSessionQuestion.session_id == session_id)
            .all()
        )
        return evaluations

    def generate_session_report(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Generates comprehensive interview session feedback report including overall score, strengths, and question breakdown."""
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied.",
            )

        all_sqs = (
            self.db.query(InterviewSessionQuestion)
            .filter(InterviewSessionQuestion.session_id == session_id)
            .order_by(InterviewSessionQuestion.sequence_number.asc())
            .all()
        )

        question_reports = []
        scores = []
        all_strengths = []
        all_improvements = []

        for sq in all_sqs:
            q_text = sq.question.question_text if sq.question else "General Question"
            ans = sq.answers[0] if sq.answers else None
            eval_obj = ans.evaluation if ans else None

            q_score = eval_obj.overall_score if eval_obj else (0.0 if sq.question_status == 'SKIPPED' else None)
            if q_score is not None and sq.question_status == 'ANSWERED':
                scores.append(q_score)

            if eval_obj:
                if eval_obj.strengths:
                    all_strengths.extend(eval_obj.strengths)
                if eval_obj.areas_to_improve:
                    all_improvements.extend(eval_obj.areas_to_improve)

            question_reports.append({
                "sequence_number": sq.sequence_number,
                "status": sq.question_status,
                "question_text": q_text,
                "score": q_score,
                "overall_feedback": eval_obj.overall_feedback if eval_obj else ("Question skipped by candidate." if sq.question_status == 'SKIPPED' else "Pending response."),
            })

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        percentage = round(avg_score * 10)
        grade = "EXCELLENT" if avg_score >= 8.0 else ("GOOD" if avg_score >= 6.0 else "NEEDS_WORK")

        unique_strengths = list(dict.fromkeys(all_strengths))[:5]
        unique_improvements = list(dict.fromkeys(all_improvements))[:5]

        return {
            "session_id": session.id,
            "interview_type": session.interview_type,
            "total_questions": session.total_questions,
            "answered_count": len(scores),
            "skipped_count": sum(1 for sq in all_sqs if sq.question_status == 'SKIPPED'),
            "overall_score": avg_score,
            "percentage": percentage,
            "grade": grade,
            "strengths": unique_strengths or ["Active participation in interview simulation."],
            "areas_to_improve": unique_improvements or ["Practice structured delivery and citing legal/policy frameworks."],
            "question_reports": question_reports,
        }
