import json
from typing import Dict, Any, Optional
from pydantic import ValidationError

from app.schemas.coach import GeminiCoachOutput, GeminiTaskItem, GeminiFocusArea
from app.services.gemini_service import BaseGeminiService, GeminiService


COACH_SYSTEM_INSTRUCTION = """You are the Prashasak AI Preparation Coach for UPSC Civil Services Interview candidates.
Analyze the candidate's actual preparation data and generate a practical, highly personalized practice plan.

STRICT REQUIREMENTS:
1. Return ONLY valid JSON adhering strictly to the required schema.
2. Do NOT invent fake test scores, statistics, or official UPSC claims.
3. Recommendations must focus on factual clarity, constitutional principles, reasoning, and policy balance.
4. Keep daily tasks realistic (3 to 6 tasks per plan, total duration 45-90 minutes).
5. Never claim questions will definitely appear in actual UPSC interviews.
6. Provide clear, evidence-based reasons for every recommendation.
"""


class RecommendationService:
    """Service generating AI-assisted structured recommendations with deterministic fallbacks."""

    def __init__(self, gemini_service: Optional[BaseGeminiService] = None):
        self.gemini_service = gemini_service or GeminiService()

    def generate_recommendations(
        self, context: Dict[str, Any], plan_type: str = "DAILY"
    ) -> GeminiCoachOutput:
        """Generate structured plan recommendations via Gemini or deterministic fallback."""
        # 1. Foundational Plan for New Candidates with No Evaluations
        if not context.get("has_evaluations", False):
            return self._build_foundational_plan(context, plan_type)

        # 2. Try Gemini Structured JSON Recommendation
        try:
            prompt = self._build_gemini_prompt(context, plan_type)
            raw_response = self.gemini_service.generate_json_response(
                prompt=prompt,
                system_instruction=COACH_SYSTEM_INSTRUCTION,
            )

            parsed_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
            output = GeminiCoachOutput(**parsed_data)

            # Validate non-empty tasks
            if output.tasks:
                return output
        except Exception:
            pass

        # 3. Deterministic Fallback Plan if Gemini is unavailable or returns malformed JSON
        return self._build_deterministic_fallback_plan(context, plan_type)

    def _build_gemini_prompt(self, context: Dict[str, Any], plan_type: str) -> str:
        return f"""
Generate a personalized {plan_type} UPSC Interview Preparation Plan for candidate '{context.get('candidate_name', 'Aspirant')}'.

CANDIDATE CONTEXT:
- DAF Profile: {json.dumps(context.get('daf', {}))}
- Overview Performance: {json.dumps(context.get('overview', {}))}
- Skill Performance: {json.dumps(context.get('skills', {}))}
- Top Topics: {json.dumps(context.get('topics', []))}
- Weak Areas: {json.dumps(context.get('weak_areas', []))}
- Strong Areas: {json.dumps(context.get('strong_areas', []))}
- Available Resources: {json.dumps(context.get('available_resources', []))}
- Current Affairs: {json.dumps(context.get('recent_current_affairs', []))}

REQUIRED JSON FORMAT:
{{
  "plan_title": "Personalized {plan_type.capitalize()} Preparation Plan",
  "summary": "Concise candidate guidance summary based on performance data.",
  "focus_areas": [
    {{
      "area": "Reasoning",
      "priority": "HIGH",
      "reason": "Evidence-based reason from weak areas"
    }}
  ],
  "tasks": [
    {{
      "task_type": "QUESTION_PRACTICE",
      "title": "Practice Policy Reasoning Questions",
      "description": "Answer 3 governance questions focusing on administrative rationale.",
      "priority": "HIGH",
      "estimated_minutes": 20,
      "source_type": "QUESTION",
      "source_id": null
    }}
  ]
}}
"""

    def _build_foundational_plan(self, context: Dict[str, Any], plan_type: str) -> GeminiCoachOutput:
        daf = context.get("daf", {})
        opt = daf.get("optional_subject") or "General Studies"

        tasks = [
            GeminiTaskItem(
                task_type="DAF_PRACTICE",
                title="Complete DAF & Profile Details",
                description=f"Review and complete your DAF profile information, especially regarding your optional subject ({opt}).",
                priority="HIGH",
                estimated_minutes=15,
                source_type="DAF",
            ),
            GeminiTaskItem(
                task_type="QUESTION_PRACTICE",
                title="Introductory Governance Question Practice",
                description="Practice answering 3 fundamental UPSC governance questions to establish baseline evaluation metrics.",
                priority="HIGH",
                estimated_minutes=20,
                source_type="QUESTION",
            ),
            GeminiTaskItem(
                task_type="CURRENT_AFFAIRS",
                title="Review Recent Current Affairs Issues",
                description="Read top 3 current affairs articles to prepare for national issue analysis.",
                priority="MEDIUM",
                estimated_minutes=15,
                source_type="CURRENT_AFFAIRS",
            ),
            GeminiTaskItem(
                task_type="INTERVIEW_PRACTICE",
                title="Complete Baseline Mock Interview Session",
                description="Take a short 3-question practice interview session to receive initial AI evaluations across 6 dimensions.",
                priority="HIGH",
                estimated_minutes=20,
                source_type="INTERVIEW",
            ),
        ]

        return GeminiCoachOutput(
            plan_title="Foundational Practice Plan",
            summary="Welcome to Prashasak AI! Complete these foundational practice tasks to establish your baseline candidate evaluation metrics.",
            focus_areas=[
                GeminiFocusArea(
                    area="Foundational Orientation",
                    priority="HIGH",
                    reason="Initial practice plan to establish candidate baseline metrics.",
                )
            ],
            tasks=tasks,
        )

    def _build_deterministic_fallback_plan(self, context: Dict[str, Any], plan_type: str) -> GeminiCoachOutput:
        weak_areas = context.get("weak_areas", [])
        topics = context.get("topics", [])
        tasks = []

        if weak_areas:
            primary_weak = weak_areas[0]["dimension"]
            tasks.append(
                GeminiTaskItem(
                    task_type="WEAK_AREA_PRACTICE",
                    title=f"Targeted Practice: {primary_weak} Improvement",
                    description=f"Focus on improving your {primary_weak} score by answering questions with explicit structured rationale.",
                    priority="HIGH",
                    estimated_minutes=20,
                    source_type="QUESTION",
                )
            )

        if topics:
            top_topic = topics[0]["topic"]
            tasks.append(
                GeminiTaskItem(
                    task_type="QUESTION_PRACTICE",
                    title=f"Practice {top_topic} Questions",
                    description=f"Answer practice questions in {top_topic} to strengthen subject domain proficiency.",
                    priority="HIGH",
                    estimated_minutes=20,
                    source_type="QUESTION",
                )
            )

        tasks.extend([
            GeminiTaskItem(
                task_type="CURRENT_AFFAIRS",
                title="Current Affairs Policy Revision",
                description="Review national governance news articles and prepare policy trade-off arguments.",
                priority="MEDIUM",
                estimated_minutes=15,
                source_type="CURRENT_AFFAIRS",
            ),
            GeminiTaskItem(
                task_type="INTERVIEW_PRACTICE",
                title="Adaptive Practice Interview Session",
                description="Complete a short mock interview session to test poise under follow-up and counter questions.",
                priority="HIGH",
                estimated_minutes=25,
                source_type="INTERVIEW",
            ),
        ])

        return GeminiCoachOutput(
            plan_title=f"Personalized {plan_type.capitalize()} Practice Plan",
            summary="Deterministic practice plan tailored to your recent answer evaluation data.",
            focus_areas=[
                GeminiFocusArea(
                    area=weak_areas[0]["dimension"] if weak_areas else "Governance & Policy",
                    priority="HIGH",
                    reason="Derived directly from your recent evaluation analytics.",
                )
            ],
            tasks=tasks,
        )
