"""
PDF Translation Service using OpenAI API
"""
import os
from typing import List, Optional
from openai import OpenAI


class TextTranslator:
    """OpenAI 기반 텍스트 번역 서비스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize translator with OpenAI API key

        Args:
            api_key: OpenAI API key (환경변수 OPENAI_API_KEY 사용 가능)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Translate text from source language to target language

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어 (예: "Korean", "English", "Japanese")
            target_lang: 대상 언어 (예: "Korean", "English", "Japanese")
            model: OpenAI 모델 (기본: gpt-4o-mini)

        Returns:
            번역된 텍스트
        """
        if not text or text.strip() == "":
            return text

        prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Only provide the translation without any explanations or additional text.

Text to translate:
{text}"""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional translator. Provide only the translation without any explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            translated_text = response.choices[0].message.content.strip()
            return translated_text

        except Exception as e:
            print(f"Translation error: {e}")
            return text  # 실패 시 원본 반환

    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        model: str = "gpt-4o-mini"
    ) -> List[str]:
        """
        Translate multiple texts in batch

        Args:
            texts: 번역할 텍스트 리스트
            source_lang: 원본 언어
            target_lang: 대상 언어
            model: OpenAI 모델

        Returns:
            번역된 텍스트 리스트
        """
        translated_texts = []

        for i, text in enumerate(texts):
            print(f"Translating text {i+1}/{len(texts)}...")
            translated = self.translate(text, source_lang, target_lang, model)
            translated_texts.append(translated)

        return translated_texts
