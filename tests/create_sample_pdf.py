"""Create a sample PDF for testing."""
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    import os

    # Create output directory
    os.makedirs("test_data", exist_ok=True)

    # Create PDF
    pdf_path = "test_data/sample.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("테스트 문서: PDF RAG 시스템", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    # Introduction
    intro = Paragraph(
        "이 문서는 PDF RAG 챗봇 시스템의 테스트를 위한 샘플 문서입니다. "
        "다양한 주제에 대한 내용을 포함하고 있습니다.",
        styles['Normal']
    )
    elements.append(intro)
    elements.append(Spacer(1, 0.3 * inch))

    # Content sections
    sections = [
        {
            "title": "1. 인공지능의 개요",
            "content": "인공지능(Artificial Intelligence, AI)은 인간의 학습능력, 추론능력, 지각능력을 "
                      "인공적으로 구현하려는 컴퓨터 과학의 세부 분야 중 하나입니다. "
                      "머신러닝, 딥러닝, 자연어처리 등 다양한 기술이 포함됩니다."
        },
        {
            "title": "2. 머신러닝의 종류",
            "content": "머신러닝은 크게 지도학습, 비지도학습, 강화학습으로 나뉩니다. "
                      "지도학습은 레이블이 있는 데이터를 사용하여 모델을 학습시킵니다. "
                      "비지도학습은 레이블 없이 데이터의 패턴을 찾아냅니다. "
                      "강화학습은 보상을 통해 최적의 행동을 학습합니다."
        },
        {
            "title": "3. 자연어처리",
            "content": "자연어처리(NLP)는 인간의 언어를 컴퓨터가 이해하고 처리할 수 있도록 하는 기술입니다. "
                      "텍스트 분류, 감정 분석, 기계 번역, 질의응답 시스템 등이 대표적인 응용 분야입니다. "
                      "최근에는 트랜스포머 기반의 대규모 언어모델이 주목받고 있습니다."
        },
        {
            "title": "4. RAG 시스템",
            "content": "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합한 시스템입니다. "
                      "먼저 관련 문서를 검색하고, 검색된 내용을 바탕으로 답변을 생성합니다. "
                      "이를 통해 LLM의 한계를 보완하고 더 정확한 답변을 제공할 수 있습니다."
        },
        {
            "title": "5. 벡터 데이터베이스",
            "content": "벡터 데이터베이스는 임베딩 벡터를 저장하고 유사도 검색을 수행하는 데이터베이스입니다. "
                      "Elasticsearch, Pinecone, Weaviate 등이 대표적입니다. "
                      "코사인 유사도나 유클리드 거리를 사용하여 관련 문서를 빠르게 찾을 수 있습니다."
        },
        {
            "title": "6. 임베딩 모델",
            "content": "임베딩 모델은 텍스트를 고차원 벡터로 변환합니다. "
                      "BERT, GPT, KURE 등 다양한 모델이 있으며, 각각 특징이 다릅니다. "
                      "한국어 처리를 위해서는 한국어 특화 모델을 사용하는 것이 효과적입니다."
        },
        {
            "title": "7. 청킹 전략",
            "content": "긴 문서를 처리하기 위해서는 적절한 크기로 분할하는 청킹이 필요합니다. "
                      "일반적으로 500-1000 토큰 크기로 청크를 만들며, 10-20% 정도 오버랩을 두어 "
                      "문맥이 끊기지 않도록 합니다."
        },
        {
            "title": "8. 프롬프트 엔지니어링",
            "content": "LLM에게 적절한 지시를 주는 것이 중요합니다. "
                      "시스템 프롬프트로 역할을 정의하고, 사용자 프롬프트에 컨텍스트를 포함시킵니다. "
                      "Few-shot learning을 활용하면 더 나은 결과를 얻을 수 있습니다."
        },
    ]

    for section in sections:
        # Section title
        section_title = Paragraph(section["title"], styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 0.1 * inch))

        # Section content
        section_content = Paragraph(section["content"], styles['Normal'])
        elements.append(section_content)
        elements.append(Spacer(1, 0.3 * inch))

    # Build PDF
    doc.build(elements)

    print(f"Sample PDF created: {pdf_path}")

except ImportError:
    print("reportlab is not installed. Install it with: pip install reportlab")
    print("Creating a simple text file instead...")

    # Fallback: create a text file with instructions
    os.makedirs("test_data", exist_ok=True)
    with open("test_data/README.txt", "w", encoding="utf-8") as f:
        f.write("샘플 PDF 생성 안내\n")
        f.write("=" * 50 + "\n\n")
        f.write("reportlab이 설치되지 않아 샘플 PDF를 생성할 수 없습니다.\n\n")
        f.write("다음 명령어로 reportlab을 설치하세요:\n")
        f.write("  pip install reportlab\n\n")
        f.write("또는 직접 테스트용 PDF 파일을 이 디렉토리에 넣어주세요.\n")

    print("Created README.txt with instructions")
