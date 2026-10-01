import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from app.core.config import settings

logger = logging.getLogger("gemini_service")


class BaseGeminiService(ABC):
    """Abstract Base Class for Gemini Generation Service."""

    @abstractmethod
    def generate_grounded_answer(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        """Generates grounded answer dictionary containing 'answer', 'grounded', and 'source_indexes'."""
        pass

    @abstractmethod
    def generate_json_response(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        """Generates structured JSON response dictionary from Gemini."""
        pass


class FakeGeminiService(BaseGeminiService):
    """
    Deterministic Mock Gemini Service for automated unit tests.
    Does not require GEMINI_API_KEY or external network connections.
    """

    def __init__(
        self,
        mock_answer: Optional[str] = None,
        mock_grounded: bool = True,
        mock_source_indexes: Optional[List[int]] = None,
        mock_json_response: Optional[Dict[str, Any]] = None,
        should_fail: bool = False,
        should_timeout: bool = False,
        should_malform: bool = False,
    ):
        self.mock_answer = mock_answer
        self.mock_grounded = mock_grounded
        self.mock_source_indexes = mock_source_indexes if mock_source_indexes is not None else [1]
        self.mock_json_response = mock_json_response
        self.should_fail = should_fail
        self.should_timeout = should_timeout
        self.should_malform = should_malform

    def generate_grounded_answer(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        if self.should_fail:
            raise RuntimeError("Simulated Gemini API 500 Internal Server Error")
        if self.should_timeout:
            raise TimeoutError("Simulated Gemini API request timeout")
        if self.should_malform:
            return {"raw_text_unparseable": "invalid json payload"}

        answer = self.mock_answer or "Grounded response based on provided context."
        return {
            "answer": answer,
            "question": answer,
            "why_this_matters": "Relevant for UPSC interview testing constitutional understanding.",
            "explanation": "Provides analytical perspective on democratic governance principles.",
            "grounded": self.mock_grounded,
            "source_indexes": self.mock_source_indexes,
        }

    def generate_json_response(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        if self.should_fail:
            raise RuntimeError("Simulated Gemini API 500 Internal Server Error")
        if self.should_timeout:
            raise TimeoutError("Simulated Gemini API request timeout")
        if self.should_malform:
            return {"raw_text_unparseable": "invalid json payload"}

        if self.mock_json_response is not None:
            return self.mock_json_response

        if "FOLLOW_UP" in system_instruction and "should_follow_up" in system_instruction:
            return {
                "should_follow_up": True,
                "reason": "Probes implementation feasibility and stakeholder trade-offs.",
                "follow_up_type": "FOLLOW_UP",
                "question": "How would you implement this policy while protecting affected stakeholders?",
            }

        if "COUNTER" in system_instruction or "should_counter" in prompt or "COUNTER" in prompt:
            return {
                "should_counter": True,
                "reason": "Challenges one-sided reasoning on administrative reform.",
                "counter_type": "COUNTER",
                "question": "How would you respond to critics who argue that this reform increases bureaucracy?",
            }

        if "Preparation Coach" in system_instruction or "Coach" in system_instruction or "CANDIDATE CONTEXT" in prompt:
            return {
                "plan_title": "Focused UPSC Preparation Plan",
                "summary": "Targeted practice plan focusing on low reasoning scores and policy analysis.",
                "focus_areas": [
                    {
                        "area": "Reasoning",
                        "priority": "HIGH",
                        "reason": "Recent evaluated answers indicate lower reasoning scores."
                    }
                ],
                "tasks": [
                    {
                        "task_type": "QUESTION_PRACTICE",
                        "title": "Practice Policy Reasoning Questions",
                        "description": "Answer 3 governance questions focusing on administrative rationale.",
                        "priority": "HIGH",
                        "estimated_minutes": 20,
                        "source_type": "QUESTION",
                        "source_id": None
                    },
                    {
                        "task_type": "CURRENT_AFFAIRS",
                        "title": "Current Affairs Policy Revision",
                        "description": "Review national governance news articles.",
                        "priority": "MEDIUM",
                        "estimated_minutes": 15,
                        "source_type": "CURRENT_AFFAIRS",
                        "source_id": None
                    }
                ]
            }

        # Extract answer text from prompt for dynamic fallback evaluation
        import re
        answer_text = ""
        match = re.search(r"Answer Text:\s*(.*?)\nDuration:", prompt, re.DOTALL)
        if match:
            answer_text = match.group(1).strip()
            
        words = answer_text.split()
        word_count = len(words)
        keyword_matches = 0
        
        if word_count == 0:
            base_score = 0.0
        else:
            base_score = min(7.0, max(2.0, word_count / 10.0))
            
            keywords = ["transparency", "accountability", "efficiency", "citizen", "public", "policy", "governance", "ethics", "rights", "democracy", "balance"]
            keyword_matches = sum(1 for kw in keywords if kw.lower() in answer_text.lower())
            
            base_score += min(3.0, keyword_matches * 0.5)
            
        base_score = min(10.0, base_score)
        variation = (len(answer_text) % 5) * 0.2
        
        c_score = min(10.0, round(base_score, 1))
        cl_score = min(10.0, round(base_score - variation, 1))
        d_score = min(10.0, round(base_score + variation, 1))
        r_score = min(10.0, round(base_score, 1))
        b_score = min(10.0, round(max(0.0, base_score - 0.5), 1))
        com_score = min(10.0, round(max(0.0, base_score + 0.5), 1))

        return {
            "content": {
                "score": c_score,
                "feedback": f"The answer contains {word_count} words and addresses some core points."
            },
            "clarity": {
                "score": cl_score,
                "feedback": "Clear structure but could be improved based on text coherence."
            },
            "depth": {
                "score": d_score,
                "feedback": "Depth is proportional to the detailed reasoning provided."
            },
            "reasoning": {
                "score": r_score,
                "feedback": "Logical progression is visible."
            },
            "balance": {
                "score": b_score,
                "feedback": "Acknowledges administrative constraints to some extent."
            },
            "communication": {
                "score": com_score,
                "feedback": "Professional and concise interview tone."
            },
            "overall_feedback": f"Dynamic evaluation based on {word_count} words. {'Good use of keywords.' if keyword_matches > 0 else 'Consider using more governance terminology.'}",
            "strengths": ["Clear structure"] if c_score > 5 else [],
            "areas_to_improve": ["Elaborate on implementation aspects"] if c_score <= 8 else [],
            "suggested_answer": "A structured answer should begin with an analytical overview followed by multi-dimensional perspective.",
        }


class GeminiService(BaseGeminiService):
    """
    Production Gemini Generation Service using the official google-genai SDK.
    Supports configurable models, exponential backoff retries, request timeout handling,
    safe error logging, and structured JSON extraction.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_GENERATION_MODEL
        self.timeout = timeout or settings.GEMINI_REQUEST_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else settings.GEMINI_MAX_RETRIES
        self._client = None

    def _get_client(self):
        if not self._client and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google.genai Client: {e}")
                self._client = None
        return self._client

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown code block formatting (```json ... ```) if present."""
        text = text.strip()
        code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            return code_block_match.group(1).strip()
        return text

    def generate_grounded_answer(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is missing. Falling back to FakeGeminiService.")
            return FakeGeminiService().generate_grounded_answer(prompt, system_instruction)

        client = self._get_client()
        if not client:
            logger.error("Gemini client initialization failed. Returning fallback.")
            return FakeGeminiService().generate_grounded_answer(prompt, system_instruction)

        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
        )

        backoff = 1.0
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Invoking Gemini model '{self.model}' (attempt {attempt + 1}/{self.max_retries})...")
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )

                if response and response.text:
                    cleaned_text = self._clean_json_text(response.text)
                    parsed_data = json.loads(cleaned_text)

                    # Validate key fields
                    if isinstance(parsed_data, dict) and ("answer" in parsed_data or "question" in parsed_data):
                        answer_str = str(parsed_data.get("answer") or parsed_data.get("question", "")).strip()
                        why_matters = str(parsed_data.get("why_this_matters", "")).strip()
                        explanation_str = str(parsed_data.get("explanation", "")).strip()
                        grounded_bool = bool(parsed_data.get("grounded", False))
                        source_indexes_raw = parsed_data.get("source_indexes", [])
                        source_indexes = (
                            [int(x) for x in source_indexes_raw if isinstance(x, (int, str)) and str(x).isdigit()]
                            if isinstance(source_indexes_raw, list)
                            else []
                        )

                        return {
                            "answer": answer_str,
                            "question": answer_str,
                            "why_this_matters": why_matters,
                            "explanation": explanation_str,
                            "grounded": grounded_bool,
                            "source_indexes": source_indexes,
                        }

                    logger.warning(f"Gemini response missing required keys: {parsed_data}")

            except json.JSONDecodeError as jde:
                logger.warning(f"Failed to parse Gemini JSON output (attempt {attempt + 1}): {jde}")
                last_exception = jde
            except Exception as e:
                err_msg = str(e)
                # Check for rate limit or transient status codes
                is_transient = any(code in err_msg for code in ["429", "500", "502", "503", "504", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "TIMEOUT"])
                logger.warning(f"Gemini API request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                last_exception = e
                if not is_transient:
                    break

            if attempt < self.max_retries - 1:
                time.sleep(backoff)
                backoff *= 2.0

        logger.error(f"Gemini API call failed after {attempt + 1} attempt(s): {last_exception}")
        raise last_exception or RuntimeError("Gemini API call failed after retries")

    def generate_json_response(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is missing. Falling back to FakeGeminiService.")
            return FakeGeminiService().generate_json_response(prompt, system_instruction)

        client = self._get_client()
        if not client:
            logger.error("Gemini client initialization failed. Returning fallback.")
            return FakeGeminiService().generate_json_response(prompt, system_instruction)

        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
        )

        backoff = 1.0
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Invoking Gemini model '{self.model}' for structured JSON response (attempt {attempt + 1}/{self.max_retries})...")
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )

                if response and response.text:
                    cleaned_text = self._clean_json_text(response.text)
                    parsed_data = json.loads(cleaned_text)
                    if isinstance(parsed_data, dict):
                        return parsed_data

                    logger.warning(f"Gemini response is not a valid JSON dict: {parsed_data}")

            except json.JSONDecodeError as jde:
                logger.warning(f"Failed to parse Gemini JSON output (attempt {attempt + 1}): {jde}")
                last_exception = jde
            except Exception as e:
                err_msg = str(e)
                is_transient = any(code in err_msg for code in ["429", "500", "502", "503", "504", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "TIMEOUT"])
                logger.warning(f"Gemini API request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                last_exception = e
                if not is_transient:
                    break

            if attempt < self.max_retries - 1:
                time.sleep(backoff)
                backoff *= 2.0

        logger.error(f"Gemini API call failed after {attempt + 1} attempt(s): {last_exception}")
        raise last_exception or RuntimeError("Gemini API call failed after retries")


def get_gemini_service(force_fake: bool = False, custom_fake: Optional[FakeGeminiService] = None) -> BaseGeminiService:
    """
    Factory function returning active Gemini generation service instance.
    Returns FakeGeminiService if force_fake is True or GEMINI_API_KEY is not configured.
    """
    if custom_fake:
        return custom_fake
    if force_fake or not settings.GEMINI_API_KEY:
        return FakeGeminiService()
    return GeminiService()
