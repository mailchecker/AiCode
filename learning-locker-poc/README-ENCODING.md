# Windows 배치 파일 한글 깨짐 문제 해결

## 문제 증상

Windows에서 `.bat` 배치 파일을 실행할 때 한글이 깨져 보이는 현상

```
? ?? ? ?? ? ?? ?
```

## 원인

- Windows CMD/PowerShell은 기본적으로 **CP949** (코드페이지 949) 인코딩 사용
- Git에서 받은 파일은 **UTF-8** 인코딩으로 저장됨
- 인코딩 불일치로 한글이 깨짐

## 해결 방법

### ✅ 방법 1: 수정된 파일 사용 (권장)

이미 모든 배치 파일에 `chcp 65001` 명령이 추가되어 있습니다!

```batch
@echo off
chcp 65001 >nul
REM 이제 한글이 정상적으로 표시됩니다
```

**Git에서 최신 버전을 받으세요:**

```powershell
git pull origin claude/learning-locker-docker-setup-L6wN0
```

### 방법 2: 수동으로 코드페이지 변경

배치 파일 실행 전 PowerShell에서:

```powershell
# UTF-8 코드페이지로 변경
chcp 65001

# 배치 파일 실행
.\start-windows.bat
```

### 방법 3: PowerShell 스크립트 사용

배치 파일 대신 PowerShell 스크립트를 사용하는 것도 방법입니다.

**start-windows.ps1** (PowerShell 버전):
```powershell
# UTF-8 출력 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================"
Write-Host "Learning Locker POC - Windows 빠른 시작"
Write-Host "============================================================"

# ... 나머지 코드 ...
```

실행:
```powershell
powershell -ExecutionPolicy Bypass -File start-windows.ps1
```

## 적용된 파일

다음 파일들에 `chcp 65001` 명령이 추가되었습니다:

- ✅ `start-windows.bat`
- ✅ `scripts/test-statements.bat`

## 확인 방법

### 현재 코드페이지 확인

```powershell
chcp
```

출력:
- `활성 코드 페이지: 949` - CP949 (한글 깨짐 가능)
- `활성 코드 페이지: 65001` - UTF-8 (한글 정상)

### 코드페이지 설명

| 코드페이지 | 이름 | 설명 |
|-----------|------|------|
| 949 | CP949 | Windows 한글 기본 인코딩 |
| 65001 | UTF-8 | 유니코드 UTF-8 인코딩 |
| 1252 | Windows-1252 | 서유럽 언어 인코딩 |

## 추가 팁

### Windows Terminal 사용 (권장)

Windows Terminal은 UTF-8을 기본으로 지원하여 한글 깨짐 문제가 거의 없습니다.

**설치:**
```powershell
# Microsoft Store에서 "Windows Terminal" 검색
# 또는
winget install Microsoft.WindowsTerminal
```

### Git Bash 사용

Git for Windows에 포함된 Git Bash도 UTF-8을 잘 지원합니다.

```bash
# Git Bash에서 실행
./start-windows.bat
```

### VS Code 통합 터미널

VS Code의 통합 터미널도 UTF-8을 기본으로 사용합니다.

1. VS Code에서 프로젝트 열기
2. `Ctrl + `` (백틱)로 터미널 열기
3. 배치 파일 실행

## 문제가 계속되는 경우

### 임시 해결책: 영어만 사용

한글 대신 영어 메시지만 출력하는 버전:

```batch
@echo off
echo ============================================================
echo Learning Locker POC - Windows Quick Start
echo ============================================================
```

### PowerShell 완전 전환

배치 파일 대신 PowerShell 스크립트(.ps1)를 사용하면 인코딩 문제가 거의 없습니다.

**요청하시면 PowerShell 버전을 제공해드리겠습니다!**

## 테스트

한글이 제대로 표시되는지 테스트:

```powershell
cd learning-locker-poc
.\start-windows.bat
```

정상 출력 예시:
```
============================================================
Learning Locker POC - Windows 빠른 시작
============================================================

[1/4] Docker 확인 완료
```

## 참고 자료

- [Windows 코드 페이지 목록](https://docs.microsoft.com/ko-kr/windows/win32/intl/code-page-identifiers)
- [chcp 명령어 설명](https://docs.microsoft.com/ko-kr/windows-server/administration/windows-commands/chcp)
- [UTF-8 인코딩 가이드](https://en.wikipedia.org/wiki/UTF-8)

---

**수정 사항이 반영된 최신 버전을 사용하시면 한글이 정상적으로 표시됩니다!** ✅
