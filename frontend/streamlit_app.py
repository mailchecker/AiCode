"""Streamlit demo UI for PDF RAG Chatbot."""
import streamlit as st
import requests
import time
import os
from typing import Optional

# API Configuration
# Try to get from secrets, fall back to environment variable, then default
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
except FileNotFoundError:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def upload_document(file, title: str, parse_provider: str):
    """Upload document to backend."""
    files = {"file": file}
    data = {"title": title, "parse_provider": parse_provider}

    response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, data=data)
    return response.json()


def get_status(doc_id: str, version_id: str):
    """Get processing status."""
    response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/versions/{version_id}/status")
    return response.json()


def list_documents():
    """List all documents."""
    response = requests.get(f"{API_BASE_URL}/documents/")
    return response.json()


def search_documents(query: str, doc_id: Optional[str] = None, top_k: int = 5):
    """Search documents."""
    payload = {"query": query, "top_k": top_k}
    if doc_id:
        payload["doc_id"] = doc_id

    response = requests.post(f"{API_BASE_URL}/search/", json=payload)
    return response.json()


def chat(query: str, doc_id: Optional[str] = None, top_k: int = 5):
    """Chat with RAG."""
    payload = {"query": query, "top_k": top_k}
    if doc_id:
        payload["doc_id"] = doc_id

    response = requests.post(f"{API_BASE_URL}/chat/", json=payload)
    return response.json()


# Page configuration
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

st.title("📚 PDF RAG Chatbot System")
st.markdown("교재 PDF를 업로드하고 AI 챗봇과 대화하세요")

# Sidebar
with st.sidebar:
    st.header("⚙️ 설정")

    # Parser selection
    parse_provider = st.selectbox(
        "PDF 파서 선택",
        ["local", "upstage"],
        help="local: 빠른 기본 파서 | upstage: 고급 AI 파서",
    )

    # Document selection
    st.header("📄 문서 목록")
    try:
        documents = list_documents()
        if documents:
            selected_doc = st.selectbox(
                "검색할 문서 선택 (전체 검색하려면 선택 안 함)",
                [None] + [f"{doc['title']} ({doc['doc_id']})" for doc in documents],
            )
            if selected_doc:
                selected_doc_id = selected_doc.split("(")[-1].rstrip(")")
            else:
                selected_doc_id = None
        else:
            st.info("업로드된 문서가 없습니다")
            selected_doc_id = None
    except Exception as e:
        st.error(f"문서 목록 로드 실패: {e}")
        selected_doc_id = None

    # Top-k setting
    top_k = st.slider("검색 결과 개수", 1, 20, 5)

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 챗봇", "🔍 검색", "📤 업로드"])

# Tab 1: Chatbot
with tab1:
    st.header("💬 AI 챗봇과 대화하기")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📎 출처 보기"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(
                            f"**[{idx}] 페이지 {source['page_start']}-{source['page_end']}**\n\n"
                            f"{source['text_snippet']}"
                        )
                        st.divider()

    # Chat input
    if prompt := st.chat_input("질문을 입력하세요..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    response = chat(prompt, doc_id=selected_doc_id, top_k=top_k)

                    answer = response["answer"]
                    sources = response["sources"]
                    has_answer = response["has_answer"]

                    # Display answer
                    st.markdown(answer)

                    # Display sources
                    if sources:
                        with st.expander("📎 출처 보기"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(
                                    f"**[{idx}] 페이지 {source['page_start']}-{source['page_end']}**\n\n"
                                    f"{source['text_snippet']}"
                                )
                                st.divider()

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as e:
                    st.error(f"오류 발생: {e}")

    # Clear chat button
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# Tab 2: Search
with tab2:
    st.header("🔍 문서 검색")

    search_query = st.text_input("검색어를 입력하세요")

    if st.button("검색", type="primary"):
        if not search_query:
            st.warning("검색어를 입력해주세요")
        else:
            with st.spinner("검색 중..."):
                try:
                    results = search_documents(search_query, doc_id=selected_doc_id, top_k=top_k)

                    st.success(f"총 {results['total']}개의 결과를 찾았습니다")

                    for idx, result in enumerate(results["results"], 1):
                        with st.expander(
                            f"**[{idx}]** 페이지 {result['page_start']}-{result['page_end']} "
                            f"(점수: {result['score']:.2f})"
                        ):
                            st.markdown(f"**문서:** {result['doc_id']}")
                            st.markdown(f"**버전:** {result['version_id']}")
                            st.markdown("**내용:**")
                            st.text_area("", result["text"], height=150, disabled=True, key=f"search_{idx}")

                except Exception as e:
                    st.error(f"검색 실패: {e}")

# Tab 3: Upload
with tab3:
    st.header("📤 PDF 업로드")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("PDF 파일 선택", type=["pdf"])
        title = st.text_input("문서 제목")

    with col2:
        st.info(
            f"**선택된 파서:** {parse_provider}\n\n"
            f"{'빠른 기본 텍스트 추출' if parse_provider == 'local' else '고급 AI 기반 파싱 (Upstage)'}"
        )

    if st.button("업로드 및 처리 시작", type="primary"):
        if not uploaded_file:
            st.warning("PDF 파일을 선택해주세요")
        elif not title:
            st.warning("문서 제목을 입력해주세요")
        else:
            with st.spinner("업로드 중..."):
                try:
                    # Upload
                    result = upload_document(uploaded_file, title, parse_provider)

                    st.success(f"✅ 업로드 성공!")
                    st.json(result)

                    doc_id = result["doc_id"]
                    version_id = result["version_id"]

                    # Monitor status
                    st.info("📊 처리 상태를 모니터링합니다...")

                    status_placeholder = st.empty()
                    progress_bar = st.progress(0)

                    max_wait = 300  # 5 minutes
                    elapsed = 0
                    interval = 3

                    while elapsed < max_wait:
                        status = get_status(doc_id, version_id)
                        current_status = status["status"]

                        status_placeholder.info(f"현재 상태: **{current_status}**")

                        if current_status == "indexed":
                            progress_bar.progress(100)
                            st.success("🎉 처리 완료! 이제 검색과 챗봇을 사용할 수 있습니다.")
                            break
                        elif current_status == "failed":
                            st.error(f"❌ 처리 실패: {status.get('error', 'Unknown error')}")
                            break
                        elif current_status == "uploaded":
                            progress_bar.progress(10)
                        elif current_status == "parsing":
                            progress_bar.progress(30)
                        elif current_status == "parsed":
                            progress_bar.progress(60)
                        elif current_status == "indexing":
                            progress_bar.progress(80)

                        time.sleep(interval)
                        elapsed += interval

                    if elapsed >= max_wait:
                        st.warning("⏰ 처리 시간이 초과되었습니다. 나중에 상태를 확인해주세요.")

                except Exception as e:
                    st.error(f"업로드 실패: {e}")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    PDF RAG Chatbot System v1.0 |
    Powered by FastAPI, Elasticsearch, Haystack, KURE-v1
    </div>
    """,
    unsafe_allow_html=True,
)
