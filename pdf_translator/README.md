# 📄 PDF Text Translation System

PDF 문서의 텍스트를 번역하면서 **원본 레이아웃을 유지**하는 시스템입니다. 이미지, 표, 도형 등은 그대로 유지하고 텍스트만 번역합니다.

## ✨ 주요 기능

- ✅ **원본 레이아웃 유지**: 텍스트 위치, 폰트, 크기 보존
- ✅ **이미지 및 표 보존**: 이미지와 표는 그대로 유지
- ✅ **다중 언어 지원**: 14개 언어 간 번역
- ✅ **페이지 범위 선택**: 전체/특정 페이지/범위 지정
- ✅ **실시간 진행 상황**: 번역 진행 상황 실시간 표시
- ✅ **고품질 번역**: OpenAI GPT 모델 사용

## 🌐 지원 언어

한국어, 영어, 일본어, 중국어(간체/번체), 프랑스어, 독일어, 스페인어, 이탈리아어, 포르투갈어, 러시아어, 아랍어, 태국어, 베트남어

## 🛠️ 기술 스택

- **PDF Processing**: PyMuPDF (fitz)
- **Translation API**: OpenAI GPT
- **Frontend**: Streamlit
- **Language**: Python 3.10+

## 📋 사전 요구사항

- Python 3.10 이상
- OpenAI API Key ([발급 방법](https://platform.openai.com/api-keys))

## 📥 GitHub에서 다운로드

### 방법 1: ZIP 파일 다운로드 (초보자 권장)

1. GitHub 저장소 페이지로 이동
2. 녹색 **Code** 버튼 클릭
3. **Download ZIP** 선택
4. 다운로드한 파일 압축 해제
5. `pdf_translator` 폴더로 이동

### 방법 2: Git Clone (Git 사용자)

```bash
git clone https://github.com/your-username/AiCode.git
cd AiCode/pdf_translator
```

> 📘 **자세한 가이드**: Windows 사용자는 [WINDOWS_SETUP.md](WINDOWS_SETUP.md)의 **GitHub에서 프로젝트 다운로드** 섹션을 참고하세요.

## 🚀 설치 및 실행

### 빠른 시작 (Windows) - 3단계로 끝!

#### 1️⃣ GitHub에서 다운로드
- GitHub 페이지에서 **Code** → **Download ZIP**
- 압축 해제 후 `pdf_translator` 폴더로 이동

#### 2️⃣ 초기 설정 (최초 1회만)
- `setup.bat` 파일 **더블클릭**
- 메모장이 열리면 OpenAI API 키 입력 후 저장

#### 3️⃣ 앱 실행
- `run.bat` 파일 **더블클릭**
- 브라우저가 자동으로 열립니다! 🎉

> 📘 **Windows 상세 가이드**: 처음 사용하시거나 문제가 있다면 [WINDOWS_SETUP.md](WINDOWS_SETUP.md)를 참고하세요. Python 설치부터 문제 해결까지 모든 내용이 담겨있습니다.

---

### 수동 설치 (Linux/macOS 또는 고급 사용자)

#### 1. 저장소 클론

```bash
cd pdf_translator
```

#### 2. 가상환경 생성 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate.bat
# Linux/macOS
source venv/bin/activate
```

#### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

#### 4. 환경변수 설정

**Linux/macOS:**
```bash
cp .env.example .env
nano .env  # 또는 원하는 에디터 사용
```

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

**.env 파일 예시:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 5. Streamlit 앱 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 사용할 수 있습니다.

## 📖 사용 방법

### 1. 언어 선택
- **Source Language (원본 언어)**: PDF의 원본 언어 선택
- **Target Language (번역 언어)**: 번역할 대상 언어 선택

### 2. 모델 선택
- **GPT-4o Mini**: 빠르고 저렴한 번역 (권장)
- **GPT-4o**: 고품질 번역
- **GPT-4 Turbo**: 최고 품질

### 3. 페이지 범위 선택

#### All Pages (전체 페이지)
모든 페이지를 번역합니다.

#### Specific Page (특정 페이지)
예시:
- `3` → 3페이지만 번역

#### Page Range (범위 지정)
예시:
- `1-10` → 1페이지부터 10페이지까지 번역
- `5-20` → 5페이지부터 20페이지까지 번역

### 4. PDF 업로드
- **Upload PDF** 영역에서 PDF 파일 선택

### 5. 번역 시작
- **Start Translation** 버튼 클릭
- 진행 상황 확인

### 6. 결과 다운로드
- 번역 완료 후 **Download Translated PDF** 버튼으로 다운로드

## 📁 프로젝트 구조

```
pdf_translator/
├── app.py                    # Streamlit 메인 앱
├── utils/
│   ├── __init__.py
│   ├── translator.py         # OpenAI 번역 서비스
│   └── pdf_processor.py      # PDF 처리 및 번역 로직
├── output/                   # 번역된 PDF 출력 디렉토리
├── requirements.txt          # Python 패키지 목록
├── .env.example             # 환경변수 템플릿
├── .gitignore               # Git 제외 파일 목록
├── setup.bat                # Windows 자동 설정 스크립트
├── run.bat                  # Windows 실행 스크립트
├── README.md                # 이 파일
└── WINDOWS_SETUP.md         # Windows 상세 설치 가이드
```

## 🔧 주요 모듈 설명

### `utils/translator.py`
OpenAI API를 사용한 텍스트 번역 서비스
- `TextTranslator`: 단일/배치 텍스트 번역 클래스

### `utils/pdf_processor.py`
PyMuPDF를 사용한 PDF 처리 및 번역
- `PDFTranslator`: PDF 파일 번역 및 레이아웃 유지 클래스
- `parse_page_range()`: 페이지 범위 파싱
- `translate_pdf()`: PDF 번역 실행

### `app.py`
Streamlit 기반 웹 인터페이스
- 언어 선택
- 페이지 범위 선택
- 파일 업로드/다운로드
- 진행 상황 표시

## 💡 사용 예시

### 예시 1: 전체 페이지 번역
```
Source Language: Korean
Target Language: English
Page Range: All Pages
```

### 예시 2: 특정 페이지만 번역
```
Source Language: English
Target Language: Japanese
Page Range: Specific Page → 5
```

### 예시 3: 범위 지정 번역
```
Source Language: Chinese (Simplified)
Target Language: Korean
Page Range: Page Range → 1-20
```

## ⚙️ 고급 설정

### 번역 품질 조정
`utils/translator.py`의 `translate()` 메서드에서 `temperature` 값 조정:
- `0.1-0.3`: 일관된 번역 (권장)
- `0.5-0.7`: 창의적인 번역

### 폰트 크기 자동 조정
`utils/pdf_processor.py`의 `translate_pdf()` 메서드에서 폰트 크기 조정 로직 수정 가능

## ⚠️ 주의사항

1. **레이아웃 제한**
   - 복잡한 레이아웃의 경우 일부 텍스트가 잘릴 수 있습니다
   - 원본 PDF의 폰트가 임베디드되지 않은 경우 기본 폰트로 대체됩니다

2. **이미지와 표**
   - 이미지 내의 텍스트는 번역되지 않습니다 (OCR 미지원)
   - 표의 구조는 유지되지만 셀 내 텍스트만 번역됩니다

3. **처리 시간**
   - 대용량 PDF는 처리 시간이 오래 걸릴 수 있습니다
   - GPT-4o Mini 모델 사용을 권장합니다

4. **API 비용**
   - OpenAI API 사용 시 비용이 발생합니다
   - 페이지 수와 텍스트 양에 따라 비용이 증가합니다

## 🐛 문제 해결

### 공통 문제

#### API 키 오류
```
⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다!
```
→ `.env` 파일에 올바른 API 키를 설정했는지 확인

#### 페이지 범위 오류
```
Invalid page range format
```
→ 페이지 범위 형식을 확인 (예: `1-10`, `5`)

#### 폰트 오류
```
Font error
```
→ PyMuPDF가 기본 폰트로 대체합니다. 정상 작동합니다.

#### 메모리 부족
대용량 PDF 처리 시 메모리 부족 발생 가능
→ 페이지 범위를 나눠서 처리

### Windows 문제

Windows 사용자는 [WINDOWS_SETUP.md](WINDOWS_SETUP.md)의 **문제 해결** 섹션을 참고하세요:

- 실행 정책 오류 (PowerShell)
- Python 명령어를 찾을 수 없음
- pip 설치 오류
- 방화벽 경고
- 포트 충돌
- 한글 경로 문제
- PyMuPDF 설치 오류

자세한 해결 방법은 [WINDOWS_SETUP.md#문제-해결](WINDOWS_SETUP.md#문제-해결)을 확인하세요.

## 📝 TODO

- [ ] OCR 지원 (이미지 내 텍스트 번역)
- [ ] 표 셀 단위 번역 개선
- [ ] 커스텀 폰트 지원
- [ ] 배치 번역 (여러 PDF 동시 처리)
- [ ] 번역 캐시 (중복 텍스트 재사용)
- [ ] PDF 미리보기 기능

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

## 📄 라이선스

MIT License

## 📧 문의

이슈가 있으면 GitHub Issues를 통해 문의해주세요.

---

Made with ❤️ using PyMuPDF, OpenAI, and Streamlit
