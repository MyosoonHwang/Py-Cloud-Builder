# ⚡ Quick Start Guide for Py-Cloud-Builder

이 가이드는 **Py-Cloud-Builder**를 로컬 환경에서 최대한 빠르게 실행하기 위한 단계별 지침입니다.

## 📋 1. 준비물 (Prerequisites)
시작하기 전에 다음 항목이 설치되어 있는지 확인해주세요.
- **Python 3.10** 이상 ([다운로드](https://www.python.org/downloads/))
- **Git** ([다운로드](https://git-scm.com/))
- **NHN Cloud 계정** (API 엔드포인트 접근 권한)

---

## 🛠️ 2. 설치 및 설정 (Setup)

### Step 1: 프로젝트 클론
터미널(PowerShell 또는 CMD)을 열고 프로젝트를 내려받습니다.
```bash
git clone [https://github.com/MyosoonHwang/Py-Cloud-Builder.git](https://github.com/MyosoonHwang/Py-Cloud-Builder.git)
cd Py-Cloud-Builder
```
### Step 2: 의존성 패키지 설치
```bash
pip install requests python-dotenv
```
### Step 3: 인증 정보 설정 (.env)
# .env 파일 내용
NHN_ID=your_email@example.com
NHN_PW=your_password
# Tenant ID는 비워두면 로그인 시 자동으로 목록을 가져옵니다.
NHN_TENANT_ID=

만약 오류가 생긴다면
NHN Cloud 콘솔에서 **Tenant ID(Project ID)**를 복사해 입력하면 정상적으로 진행됩니다.

🚀 3. 실행 (Run)
설정이 완료되었다면 main.py를 실행합니다.
```Bash
py main.py
```