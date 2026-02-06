# ☁️ NHN Cloud Network Builder (Py-Cloud-Builder)

**NHN Cloud (OpenStack 기반)** 환경에서 VPC, 서브넷, 그리고 Bastion 서버를 쉽고 안전하게 관리하는 **All-in-One 파이썬 자동화 도구**입니다.

복잡한 NHN Cloud 콘솔에 접속할 필요 없이, **직관적인 웹 GUI**를 통해 리소스를 조회하고, 중복 걱정 없이 네트워크를 구축하며, **웹 브라우저에서 바로 SSH 터미널**을 사용할 수 있습니다.

## ✨ 주요 기능 (Key Features)

### 1. 🔐 스마트 하이브리드 인증
* **자동 프로젝트 검색:** 아이디/비밀번호만 입력하면 참여 중인 프로젝트(Tenant)를 자동으로 찾아 연결합니다.
* **유연한 접속:** 자동 조회가 실패할 경우, Tenant ID 수동 입력 모드로 전환되어 끊김 없는 작업을 지원합니다.
* **.env 지원:** 환경 변수 파일을 통해 매번 로그인할 필요 없는 **원터치 로그인**을 제공합니다.

### 2. 🛡️ 강력한 유효성 검사 & 중복 방지
* **CIDR 충돌 방지:** 기존 VPC 및 공용 네트워크 대역을 분석하여, 겹치지 않는 안전한 IP 대역인지 자동으로 계산합니다.
* **이름 중복 방지:** 이미 존재하는 리소스 이름의 재사용을 막아 운영 실수를 방지합니다.
* **Scope 검증:** 서브넷 생성 시, 상위 VPC의 CIDR 범위를 벗어나는지 실시간으로 검사합니다.

### 3. 📊 직관적인 리소스 시각화
* **트리 뷰 (Tree View):** VPC와 그 하위 서브넷 구조를 계층형으로 한눈에 파악할 수 있습니다.
* **스마트 필터링:** `Public Network`나 다른 프로젝트의 리소스는 제외하고, **내 프로젝트의 리소스**만 깔끔하게 보여줍니다.

### 4. 🚀 Bastion 호스트 & 웹 터미널 (New!)
* **원클릭 접속:** 복잡한 Floating IP 연결, 보안 그룹(22번 포트) 설정을 버튼 하나로 자동화합니다.
* **WebSSH 내장:** 별도의 터미널 프로그램(Putty, Xshell) 없이, **웹 브라우저 안에서 즉시 실행되는 진짜 리눅스 터미널**을 제공합니다.
* **키 파일 관리:** PEM 키 파일을 드래그 앤 드롭하여 간편하게 인증할 수 있습니다.

---

## 🛠️ 기술 스택 (Tech Stack)
* **Language:** Python 3.10+
* **UI Framework:** PyWebIO (Web GUI)
* **Network & API:** Requests (OpenStack API)
* **SSH & Terminal:** Paramiko, WebSSH

---

## ❗ 트러블슈팅 (FAQ)

**Q. 401 Client Error 또는 인증 실패가 뜹니다.**
> A. NHN Cloud 웹사이트 로그인 비밀번호가 아닌, **API 비밀번호**를 사용해야 할 수 있습니다.
> * 확인 경로: `NHN Cloud 콘솔` > `우측 상단 회원 아이콘` > `API 보안 설정` > `API 비밀번호 설정`

**Q. 자동 조회가 실패하고 Tenant ID를 입력하라고 합니다.**
> A. 계정 권한 문제로 프로젝트 목록 조회가 막힌 경우입니다. NHN Cloud 콘솔 URL이나 정보란에서 **Tenant ID (Project ID)** 32자리를 복사해 입력하면 정상 작동합니다.

**Q. SSH 접속 시 'Connection Refused'가 뜹니다.**
> A. Bastion 서버의 보안 그룹에 **내 PC의 IP(22번 포트)**가 허용되어 있는지 확인하세요. (이 툴의 'Bastion 접속' 기능은 이를 자동으로 처리해 줍니다.)

---

## 🧑‍💻 Developer
* **Name:** Hwang Woo Hyeok
* **Contact:** [GitHub Profile](https://github.com/MyosoonHwang)


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

### NHN ID 입력
NHN_ID="ex_your_email@example.com 또는 ID"

### API 비밀번호 (콘솔 > 회원정보 > API 보안 설정에서 발급 추천)
NHN_PW="ex_password"

#### 테넌트 ID 입력
NHN_TENANT_ID=" "

🚀 실행 방법 (How to Run)
[중요] 웹 터미널(WebSSH)과 메인 화면을 동시에 사용하기 위해 터미널을 2개 띄워야 합니다.

### Step 1: WebSSH 서버 실행 (터미널 1)
첫 번째 터미널을 열고 아래 명령어를 입력하여 백그라운드 SSH 서버를 켭니다. (이 터미널은 끄지 말고 켜두세요!) (ctrl + `)

```Bash
python -m webssh.main --port=8888
```
### Step 2: 메인 웹 서버 실행 (터미널 2)
새로운 터미널(+ 버튼)을 열고 메인 프로그램을 실행합니다.

```Bash
python web.py
```
Step 3: 접속
브라우저가 자동으로 열리지 않으면 아래 주소로 접속하세요.

주소: http://localhost:8081