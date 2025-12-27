"""LLM service for RAG chat."""
from openai import OpenAI
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM generation using OpenAI."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    def generate_answer(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer using LLM based on retrieved contexts.

        Args:
            query: User question
            contexts: List of retrieved context chunks

        Returns:
            Dict with 'answer' and 'has_answer'
        """
        if not contexts:
            return {
                "answer": "죄송합니다. 질문과 관련된 내용을 교재에서 찾을 수 없습니다.",
                "has_answer": False,
            }

        # Build context string
        context_parts = []
        for idx, ctx in enumerate(contexts):
            context_parts.append(
                f"[문서 {idx + 1}] (페이지 {ctx['page_start']}-{ctx['page_end']})\n{ctx['text']}\n"
            )
        context_str = "\n".join(context_parts)

        # Build prompt
        system_prompt = """당신은 교재 내용을 기반으로 질문에 답변하는 AI 어시스턴트입니다.

중요한 규칙:
1. 제공된 교재 내용만을 기반으로 답변하세요.
2. 교재에 없는 내용은 절대 추측하거나 외부 지식을 사용하지 마세요.
3. 답변할 수 없는 경우 "교재에서 관련 내용을 찾을 수 없습니다"라고 명확히 밝히세요.
4. 답변 시 가능한 한 구체적으로, 교재의 어느 부분에서 찾았는지 페이지를 언급하세요.
5. 한국어로 정확하고 명확하게 답변하세요."""

        user_prompt = f"""다음 교재 내용을 참고하여 질문에 답변해주세요:

<교재 내용>
{context_str}
</교재 내용>

<질문>
{query}
</질문>

교재 내용을 기반으로 답변해주세요. 교재에 없는 내용이면 "교재에서 관련 내용을 찾을 수 없습니다"라고 답변하세요."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            answer = response.choices[0].message.content.strip()

            # Check if LLM indicated no answer found
            no_answer_indicators = [
                "교재에서 관련 내용을 찾을 수 없습니다",
                "교재에 없는 내용",
                "제공된 내용에서 찾을 수 없",
            ]
            has_answer = not any(indicator in answer for indicator in no_answer_indicators)

            logger.info(f"Generated answer for query: {query[:50]}... (has_answer={has_answer})")

            return {
                "answer": answer,
                "has_answer": has_answer,
            }

        except Exception as e:
            logger.error(f"Error generating LLM answer: {e}")
            return {
                "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                "has_answer": False,
            }


# Global instance
llm_service = LLMService()
