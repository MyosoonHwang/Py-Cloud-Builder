# ⚡ Quick Start Guide

이 가이드는 **Py-Cloud-Builder**를 로컬 환경에서 즉시 실행하기 위한 단계별 지침입니다.

## 📋 1. 준비물 (Prerequisites)
* **Python 3.10** 이상
* **Git**
* **NHN Cloud 계정** (API 비밀번호 권장)

## 🚀 2. 설치 및 실행 (Setup & Run)

### Step 1: 프로젝트 클론
터미널(PowerShell, CMD, Terminal)을 열고 프로젝트를 다운로드합니다.
```bash
git clone [https://github.com/MyosoonHwang/Py-Cloud-Builder.git](https://github.com/MyosoonHwang/Py-Cloud-Builder.git)
cd Py-Cloud-Builder
```

### Step 2: 필수 패키지 설치
```bash
pip install -r requirements.txt
```
### Step 3: 인증 정보 설정 (.env)
프로젝트 폴더 안에 .env 파일을 만들고 아래 내용을 채워넣으세요.

# NHN Cloud 이메일 아이디
NHN_ID=your_email@example.com

# API 비밀번호 (콘솔 > 회원정보 > API 보안 설정에서 발급 추천)
NHN_PW=your_api_password

# (선택사항) 특정 프로젝트 ID로 고정하고 싶을 때만 입력
NHN_TENANT_ID=

### Step 4: 프로그램 실행
GUI 웹 서버를 실행합니다.
```bash
python web.py
```