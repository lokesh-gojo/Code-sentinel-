from typing import List, Optional
from app.models.schemas import Finding
from app.services.llm_provider import (
    llm_factory,
    StructuredPatchOutput,
)


class AIReviewerService:
    """
    Facade for AI Code Review and Patch Generation.
    Delegates to the configured multi-LLM provider (Gemini, Ollama, or Heuristic fallback).
    """

    def generate_fix_and_test(
        self,
        code: str,
        filename: str,
        findings: List[Finding],
        previous_error: Optional[str] = None,
        project_context: Optional[str] = None,
        provider_preference: str = "auto",
    ) -> StructuredPatchOutput:
        provider = llm_factory.get_provider(provider_preference)
        return provider.generate_patch(
            code=code,
            filename=filename,
            findings=findings,
            previous_error=previous_error,
            project_context=project_context,
        )

    def chat_assist(
        self,
        prompt: str,
        repo_context: Optional[str] = None,
        findings: Optional[List[Finding]] = None,
        provider_preference: str = "auto",
    ) -> str:
        provider = llm_factory.get_provider(provider_preference)
        return provider.chat_assist(
            prompt=prompt,
            repo_context=repo_context,
            findings=findings,
        )


ai_reviewer_service = AIReviewerService()
