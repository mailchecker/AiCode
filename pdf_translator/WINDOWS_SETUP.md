# 📘 Windows 설치 및 구동 가이드

Windows 환경에서 PDF Translation System을 설치하고 실행하는 상세 가이드입니다.

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [Python 설치](#python-설치)
3. [프로젝트 설정](#프로젝트-설정)
4. [빠른 시작 (자동 스크립트)](#빠른-시작-자동-스크립트)
5. [수동 설정 (단계별)](#수동-설정-단계별)
6. [실행 방법](#실행-방법)
7. [문제 해결](#문제-해결)

---

## 사전 요구사항

### 필수 사항

- ✅ Windows 10 이상
- ✅ OpenAI API Key ([발급 방법](https://platform.openai.com/api-keys))
- ✅ 인터넷 연결

### 권장 사항

- 💾 최소 2GB 여유 디스크 공간
- 🧠 최소 4GB RAM

---

## Python 설치

### 방법 1: Microsoft Store (권장)

1. **Microsoft Store 열기**
   - Windows 키 + `S` → "Microsoft Store" 검색

2. **Python 검색 및 설치**
   - Store에서 "Python 3.12" 또는 "Python 3.11" 검색
   - "Python 3.12" 클릭 → **설치** 버튼 클릭
   - 설치 완료까지 대기

3. **설치 확인**
   ```cmd
   python --version
   ```
   - 출력 예시: `Python 3.12.0`

### 방법 2: python.org (직접 다운로드)

1. **Python 다운로드**
   - https://www.python.org/downloads/ 접속
   - "Download Python 3.12.x" 버튼 클릭

2. **설치 실행**
   - 다운로드한 설치 파일 실행
   - ⚠️ **중요**: "Add Python to PATH" 체크박스 **반드시 선택**
   - "Install Now" 클릭

3. **설치 확인**
   - 명령 프롬프트 열기 (Windows 키 + R → `cmd` 입력)
   ```cmd
   python --version
   pip --version
   ```

---

## 프로젝트 설정

### 1. 프로젝트 폴더로 이동

```cmd
cd pdf_translator
```

또는 파일 탐색기에서:
- `pdf_translator` 폴더로 이동
- 주소창에 `cmd` 입력 → Enter (해당 위치에서 명령 프롬프트 열림)

---

## 빠른 시작 (자동 스크립트)

Windows 배치 파일을 사용하여 자동으로 설정하고 실행할 수 있습니다.

### 1. 초기 설정 (최초 1회만)

`setup.bat` 파일을 **더블클릭**하거나:

```cmd
setup.bat
```

이 스크립트는 자동으로:
- ✅ 가상환경 생성
- ✅ 패키지 설치
- ✅ .env 파일 생성

### 2. 앱 실행

`run.bat` 파일을 **더블클릭**하거나:

```cmd
run.bat
```

브라우저가 자동으로 열립니다! 🎉

---

## 수동 설정 (단계별)

자동 스크립트가 작동하지 않는 경우 수동으로 설정합니다.

### 1. 가상환경 생성

```cmd
python -m venv venv
```

### 2. 가상환경 활성화

```cmd
venv\Scripts\activate
```

✅ 성공 시 프롬프트 앞에 `(venv)` 표시됩니다:
```
(venv) C:\Users\YourName\pdf_translator>
```

❌ 오류 발생 시 ([문제 해결](#실행-정책-오류) 참고):
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. 패키지 설치

```cmd
pip install -r requirements.txt
```

설치 진행 상황이 표시됩니다. 완료까지 1-3분 소요됩니다.

### 4. 환경변수 설정

#### .env 파일 생성

```cmd
copy .env.example .env
```

#### .env 파일 편집

**방법 1: 메모장 사용**
```cmd
notepad .env
```

**방법 2: 파일 탐색기**
- `pdf_translator` 폴더에서 `.env` 파일 찾기
- 마우스 오른쪽 클릭 → **연결 프로그램** → **메모장**

#### API 키 입력

`.env` 파일에 다음과 같이 입력:
```
OPENAI_API_KEY=sk-proj-your_actual_api_key_here
```

⚠️ `your_actual_api_key_here`를 실제 API 키로 교체하세요!

파일 저장 (Ctrl + S) 후 닫기

---

## 실행 방법

### 방법 1: 배치 파일 사용 (권장)

**`run.bat` 더블클릭**

또는 명령 프롬프트에서:
```cmd
run.bat
```

### 방법 2: 수동 실행

1. **가상환경 활성화**
   ```cmd
   venv\Scripts\activate
   ```

2. **Streamlit 앱 실행**
   ```cmd
   streamlit run app.py
   ```

3. **브라우저 열기**
   - 자동으로 열리지 않으면: http://localhost:8501

### 앱 종료

- 명령 프롬프트에서: `Ctrl + C`
- 또는 명령 프롬프트 창 닫기

---

## 문제 해결

### 1. 실행 정책 오류

**오류 메시지:**
```
venv\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결 방법:**

#### PowerShell 사용 시

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

그 후 다시:
```powershell
venv\Scripts\Activate.ps1
```

#### 또는 명령 프롬프트(cmd) 사용

PowerShell 대신 명령 프롬프트 사용:
```cmd
venv\Scripts\activate.bat
```

### 2. Python 명령어를 찾을 수 없음

**오류 메시지:**
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결 방법:**

1. **Python 재설치**
   - python.org에서 다운로드
   - 설치 시 "Add Python to PATH" 체크

2. **환경 변수 수동 설정**
   - Windows 키 → "환경 변수" 검색
   - "시스템 환경 변수 편집" 클릭
   - "환경 변수" 버튼 클릭
   - "Path" 선택 → "편집" 클릭
   - Python 설치 경로 추가:
     ```
     C:\Users\YourName\AppData\Local\Programs\Python\Python312
     C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts
     ```

3. **명령 프롬프트 재시작**

### 3. pip 설치 오류

**오류 메시지:**
```
Could not install packages due to an EnvironmentError
```

**해결 방법:**

1. **pip 업그레이드**
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **관리자 권한으로 실행**
   - 명령 프롬프트를 **관리자 권한으로 실행**
   - Windows 키 → `cmd` 검색 → 마우스 오른쪽 클릭 → "관리자 권한으로 실행"

3. **캐시 삭제 후 재설치**
   ```cmd
   pip cache purge
   pip install -r requirements.txt
   ```

### 4. 방화벽 경고

**경고 메시지:**
```
Windows 보안 경고: Windows Defender 방화벽이 일부 기능을 차단했습니다
```

**해결 방법:**

- **"액세스 허용"** 버튼 클릭
- Streamlit 앱이 로컬 네트워크에서만 실행되므로 안전합니다

### 5. 포트 충돌 오류

**오류 메시지:**
```
OSError: [Errno 10048] error while attempting to bind on address...
```

**해결 방법:**

1. **다른 포트 사용**
   ```cmd
   streamlit run app.py --server.port 8502
   ```

2. **사용 중인 포트 종료**
   ```cmd
   netstat -ano | findstr :8501
   taskkill /PID <프로세스ID> /F
   ```

### 6. API 키 인식 오류

**오류 메시지:**
```
⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다!
```

**해결 방법:**

1. **.env 파일 확인**
   - 파일이 `pdf_translator` 폴더에 있는지 확인
   - 파일명이 정확히 `.env`인지 확인 (`.env.txt` 아님!)

2. **파일 확장자 표시 설정**
   - 파일 탐색기 → 보기 → "파일 확장명" 체크

3. **.env 파일 내용 확인**
   ```cmd
   type .env
   ```
   출력:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```

4. **앱 재시작**
   - Streamlit 앱 종료 (Ctrl + C)
   - 다시 실행

### 7. 한글 경로 문제

**문제:**
사용자 이름이나 경로에 한글이 포함된 경우 오류 발생 가능

**해결 방법:**

1. **영문 경로로 이동**
   ```cmd
   C:\projects\pdf_translator
   ```
   한글이 없는 경로에 프로젝트 복사

2. **또는 가상환경을 영문 경로에 생성**
   ```cmd
   python -m venv C:\venv_pdf
   C:\venv_pdf\Scripts\activate
   ```

### 8. PyMuPDF 설치 오류

**오류 메시지:**
```
ERROR: Failed building wheel for PyMuPDF
```

**해결 방법:**

1. **Microsoft Visual C++ 재배포 패키지 설치**
   - https://aka.ms/vs/17/release/vc_redist.x64.exe 다운로드 및 설치

2. **재설치 시도**
   ```cmd
   pip install --upgrade PyMuPDF
   ```

### 9. Streamlit 앱이 열리지 않음

**문제:**
명령어 실행 후 브라우저가 자동으로 열리지 않음

**해결 방법:**

1. **수동으로 브라우저 열기**
   - 주소창에 입력: `http://localhost:8501`

2. **네트워크 설정 확인**
   ```cmd
   streamlit run app.py --server.headless false
   ```

---

## 📝 편리한 사용 팁

### 바탕화면 바로가기 만들기

1. **run.bat 파일 찾기**
   - `pdf_translator` 폴더에서 `run.bat` 파일

2. **바로가기 생성**
   - `run.bat` 파일에 마우스 오른쪽 클릭
   - "바로가기 만들기" 선택
   - 바로가기를 바탕화면으로 이동

3. **아이콘 변경 (선택사항)**
   - 바로가기에 마우스 오른쪽 클릭 → "속성"
   - "아이콘 변경" 클릭

### 시작 메뉴에 추가

1. **run.bat 바로가기 복사**
2. **시작 메뉴 폴더로 이동**
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs
   ```
3. **바로가기 붙여넣기**

---

## 🔄 업데이트 방법

새 버전으로 업데이트할 때:

```cmd
REM 가상환경 활성화
venv\Scripts\activate

REM 패키지 업데이트
pip install -r requirements.txt --upgrade

REM 앱 재실행
streamlit run app.py
```

---

## 🗑️ 완전 제거

프로그램을 완전히 제거하려면:

1. **가상환경 비활성화**
   ```cmd
   deactivate
   ```

2. **프로젝트 폴더 삭제**
   - `pdf_translator` 폴더를 휴지통으로 이동

3. **Python 제거 (선택사항)**
   - 설정 → 앱 → Python → 제거

---

## 📞 추가 도움말

### 유용한 명령어

```cmd
REM Python 버전 확인
python --version

REM pip 버전 확인
pip --version

REM 설치된 패키지 목록
pip list

REM 가상환경 비활성화
deactivate

REM 현재 디렉토리 확인
cd

REM 파일 목록 보기
dir
```

### 로그 확인

Streamlit 실행 시 오류 메시지가 명령 프롬프트에 표시됩니다.
- 오류 발생 시 메시지를 복사하여 검색하거나 이슈로 등록해주세요.

---

## ✅ 체크리스트

설치가 완료되었는지 확인하세요:

- [ ] Python 설치 완료 (`python --version` 실행 성공)
- [ ] 가상환경 생성 완료 (`venv` 폴더 존재)
- [ ] 패키지 설치 완료 (`pip list`에서 PyMuPDF, streamlit, openai 확인)
- [ ] `.env` 파일 생성 및 API 키 입력 완료
- [ ] Streamlit 앱 실행 성공 (브라우저에서 앱 확인)

---

## 🎉 설치 완료!

모든 설정이 완료되었습니다!

이제 `run.bat`를 더블클릭하여 언제든지 PDF 번역 시스템을 사용할 수 있습니다.

문제가 발생하면 [문제 해결](#문제-해결) 섹션을 참고하거나 GitHub Issues에 문의해주세요.

**즐거운 번역 되세요! 📄✨**
