"""
Streamlit App for PDF Translation
"""
import streamlit as st
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from utils.translator import TextTranslator
from utils.pdf_processor import PDFTranslator
from utils.pdf_processor_v2 import PDFTranslatorV2

# .env 파일 로드
load_dotenv(encoding='utf-8')


# 페이지 설정
st.set_page_config(
    page_title="PDF Translation System",
    page_icon="📄",
    layout="wide"
)

# 지원 언어 목록
LANGUAGES = {
    "Korean": "한국어",
    "English": "영어",
    "Japanese": "일본어",
    "Chinese (Simplified)": "중국어 (간체)",
    "Chinese (Traditional)": "중국어 (번체)",
    "French": "프랑스어",
    "German": "독일어",
    "Spanish": "스페인어",
    "Italian": "이탈리아어",
    "Portuguese": "포르투갈어",
    "Russian": "러시아어",
    "Arabic": "아랍어",
    "Thai": "태국어",
    "Vietnamese": "베트남어"
}

# OpenAI 모델 목록
MODELS = {
    "GPT-4o Mini (빠르고 저렴)": "gpt-4o-mini",
    "GPT-4o (고품질)": "gpt-4o",
    "GPT-4 Turbo": "gpt-4-turbo-preview"
}


def main():
    st.title("📄 PDF Text Translation System")
    st.markdown("---")

    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
        st.info("💡 .env 파일을 생성하여 OPENAI_API_KEY를 설정해주세요.")
        st.code("OPENAI_API_KEY=your_api_key_here")
        return

    st.success("✅ OpenAI API Key 확인 완료")

    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ Translation Settings")

        # 언어 선택
        st.subheader("🌐 Languages")
        source_lang_display = st.selectbox(
            "Source Language (원본 언어)",
            options=list(LANGUAGES.keys()),
            index=1,  # 기본값: English (영어)
            format_func=lambda x: f"{LANGUAGES[x]} ({x})"
        )

        target_lang_display = st.selectbox(
            "Target Language (번역 언어)",
            options=list(LANGUAGES.keys()),
            index=0,  # 기본값: Korean (한국어)
            format_func=lambda x: f"{LANGUAGES[x]} ({x})"
        )

        # 모델 선택
        st.subheader("🤖 Model")
        model_display = st.selectbox(
            "OpenAI Model",
            options=list(MODELS.keys())
        )
        model = MODELS[model_display]

        # 처리 엔진 선택
        st.subheader("⚙️ Processing Engine")
        engine_version = st.radio(
            "Select Engine",
            options=["V2 (Professional - Span-level)", "V1 (Legacy - Block-level)"],
            index=0,
            help="V2: Professional grade with precise positioning\nV1: Legacy version with block-level processing"
        )
        use_v2 = engine_version.startswith("V2")

        # 페이지 범위 선택
        st.subheader("📑 Page Range")
        page_range_type = st.radio(
            "Select Range Type",
            options=["All Pages", "Specific Page", "Page Range"],
            horizontal=True
        )

        if page_range_type == "Specific Page":
            page_num = st.number_input(
                "Page Number",
                min_value=1,
                value=1,
                step=1
            )
            page_range = str(page_num)
        elif page_range_type == "Page Range":
            col1, col2 = st.columns(2)
            with col1:
                start_page = st.number_input(
                    "From",
                    min_value=1,
                    value=1,
                    step=1
                )
            with col2:
                end_page = st.number_input(
                    "To",
                    min_value=1,
                    value=1,
                    step=1
                )
            page_range = f"{start_page}-{end_page}"
        else:
            page_range = "ALL"

        st.info(f"📄 Page Range: **{page_range}**")

    # 메인 영역
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Select a PDF file to translate"
        )

        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📦 File size: {uploaded_file.size / 1024:.2f} KB")

    with col2:
        st.subheader("📥 Download Translated PDF")

        if "translated_file_path" in st.session_state:
            with open(st.session_state.translated_file_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Translated PDF",
                    data=f,
                    file_name=st.session_state.translated_file_name,
                    mime="application/pdf",
                    type="primary"
                )
            st.success("✅ Translation completed!")
        else:
            st.info("ℹ️ Translated PDF will appear here after processing")

    # 번역 실행 버튼
    st.markdown("---")

    if uploaded_file:
        if st.button("🚀 Start Translation", type="primary", use_container_width=True):
            try:
                # 진행 상황 표시
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 임시 파일 생성
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
                    tmp_input.write(uploaded_file.read())
                    input_path = tmp_input.name

                # 출력 파일 경로
                output_dir = Path("pdf_translator/output")
                output_dir.mkdir(parents=True, exist_ok=True)

                original_name = Path(uploaded_file.name).stem
                output_filename = f"{original_name}_translated_{source_lang_display[:2].lower()}_to_{target_lang_display[:2].lower()}.pdf"
                output_path = output_dir / output_filename

                # 번역기 초기화
                status_text.text("🔧 Initializing translator...")
                translator = TextTranslator(api_key=api_key)

                if use_v2:
                    pdf_translator = PDFTranslatorV2(translator)
                    status_text.text("🔧 Using V2 Professional Engine...")
                else:
                    pdf_translator = PDFTranslator(translator)
                    status_text.text("🔧 Using V1 Legacy Engine...")

                # 진행 상황 콜백
                def progress_callback(current_page, total_pages):
                    progress = current_page / total_pages
                    progress_bar.progress(progress)
                    status_text.text(f"📄 Processing page {current_page}/{total_pages}...")

                # 번역 실행
                status_text.text("🌐 Translating PDF...")

                pdf_translator.translate_pdf(
                    input_path=input_path,
                    output_path=str(output_path),
                    source_lang=source_lang_display,
                    target_lang=target_lang_display,
                    page_range=page_range,
                    progress_callback=progress_callback
                )

                # 완료
                progress_bar.progress(1.0)
                status_text.text("✅ Translation complete!")

                # 세션 상태에 저장
                st.session_state.translated_file_path = str(output_path)
                st.session_state.translated_file_name = output_filename

                # 임시 파일 삭제
                os.unlink(input_path)

                # 페이지 새로고침
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during translation: {str(e)}")
                st.exception(e)
    else:
        st.warning("⚠️ Please upload a PDF file first")

    # 하단 정보
    st.markdown("---")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        ### 사용 방법

        1. **환경 설정**
           - `.env` 파일에 `OPENAI_API_KEY` 설정

        2. **언어 선택**
           - 원본 언어(Source Language)와 번역 언어(Target Language) 선택

        3. **페이지 범위 선택**
           - **All Pages**: 전체 페이지 번역
           - **Specific Page**: 특정 페이지만 번역 (예: 3페이지)
           - **Page Range**: 범위 지정 번역 (예: 1-10페이지)

        4. **PDF 업로드**
           - PDF 파일을 업로드

        5. **번역 시작**
           - "Start Translation" 버튼 클릭

        6. **결과 다운로드**
           - 번역 완료 후 "Download Translated PDF" 버튼으로 다운로드

        ### 주의사항

        - 이미지, 표, 도형은 원본 그대로 유지됩니다
        - 텍스트만 번역되며, 원본 위치와 레이아웃을 최대한 유지합니다
        - 복잡한 레이아웃의 경우 일부 텍스트가 잘릴 수 있습니다
        - 대용량 PDF는 처리 시간이 오래 걸릴 수 있습니다
        """)

    with st.expander("🔧 Technical Details"):
        st.markdown("""
        ### 기술 스택

        - **PDF Processing**: PyMuPDF (fitz)
        - **Translation API**: OpenAI GPT
        - **Frontend**: Streamlit
        - **Language**: Python 3.10+

        ### 특징

        - ✅ 원본 레이아웃 유지
        - ✅ 이미지 및 표 보존
        - ✅ 다중 언어 지원
        - ✅ 페이지 범위 선택
        - ✅ 실시간 진행 상황 표시
        """)


if __name__ == "__main__":
    main()
