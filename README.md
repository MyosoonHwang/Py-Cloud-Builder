# ☁️ Py-Cloud-Builder (Multi-Cloud Network Automator)

> **Python을 활용한 Azure & NHN Cloud 네트워크 리소스 자동 생성 및 시각화 도구**

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4?logo=microsoft-azure&logoColor=white)
![NHN Cloud](https://img.shields.io/badge/Cloud-NHN_Cloud_(OpenStack)-blue?logo=openstack&logoColor=white)

## 📖 프로젝트 개요 (Project Overview)
**Py-Cloud-Builder**는 복잡한 클라우드 CLI 명령어(`az`, `openstack`)를 직접 입력하지 않고, 인터랙티브한 대화형 인터페이스를 통해 쉽고 안전하게 네트워크 리소스를 생성해 주는 자동화 도구입니다.

단순 생성뿐만 아니라, **생성될 네트워크 구조(Topology)를 트리 형태로 미리 시각화(Preview)**하여 설계 오류를 방지할 수 있도록 돕습니다.

### 💡 개발 동기
클라우드 인프라 구축 시 반복되는 CLI 명령어 입력의 번거로움과 휴먼 에러(오타)를 줄이기 위해 개발했습니다. 특히 '혼자 공부하는 파이썬' 학습 내용을 바탕으로, 외부 라이브러리 없이 순수 Python 기본 문법(List, Dictionary, Subprocess)만으로 실무적인 도구를 구현하는 데 초점을 맞췄습니다.

---

## 🚀 주요 기능 (Key Features)

1.  **Multi-Cloud 지원**: 하나의 스크립트로 **Azure**와 **NHN Cloud(OpenStack)** 환경을 모두 지원합니다.
2.  **Topology Visualization**: 리소스 생성 전, VNet(VPC)과 서브넷의 구조를 트리(Tree) 형태의 그래픽으로 보여줍니다.
3.  **CLI Wrapper**: Python의 `subprocess` 모듈을 활용하여 시스템에 설치된 Native CLI 도구를 직접 제어합니다.
4.  **Safety First**: '미리보기 -> 사용자 승인 -> 실행'의 3단계 절차를 통해 실수로 인한 과금을 방지합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language**: Python 3
* **Libraries**: `subprocess`, `sys`, `time` (Built-in Standard Libraries only)
* **Infrastructure**: Azure CLI (`az`), OpenStack CLI (`openstack`)

---

## 💻 사용 방법 (Usage)

### 1. 사전 요구 사항 (Prerequisites)
이 도구를 실행하기 위해서는 타겟 클라우드의 CLI 도구가 설치되어 있어야 합니다.

* **Azure**: [Azure CLI 설치](https://learn.microsoft.com/ko-kr/cli/azure/install-azure-cli) 및 `az login` 완료
* **NHN Cloud**: OpenStack CLI 설치 및 API 환경 변수 설정

### 2. 실행 (Run)
터미널에서 아래 명령어를 입력하여 프로그램을 시작합니다.

```bash
python main.py

3. 실행 예시 (Example)

[🚀 Azure VNet 생성 마법사 시작]
--------------------------------------------------
1. 리소스 그룹 이름 (예: RG-Test): MyResourceGroup
2. 생성할 VNet 이름 (예: MyVNet): Core-VNet
... (서브넷 정보 입력) ...

[ 🗺️ NETWORK TOPOLOGY PREVIEW ]
Cloud: Azure
 ┗━━ ☁️  Virtual Network: [Core-VNet]
       │   Resource Group: MyResourceGroup
       │   CIDR Block:     10.0.0.0/16
       │
       ┣━━ 📂 Subnet: [Web-Subnet] (10.0.1.0/24)
       ┗━━ 📂 Subnet: [DB-Subnet] (10.0.2.0/24)

위 구조대로 생성을 진행하시겠습니까? (yes/no): yes

📂 파일 구조 (File Structure)
Py-Cloud-Builder/
├── main.py        # 메인 소스 코드 (입력, 시각화, CLI 실행 로직 포함)
└── README.md      # 프로젝트 설명서

👤 작성자 (Author)
황우혁 (Hwang Woo Hyeok)

Computer Science, Soongsil Univ.

Email: (이메일: woohek00@gmail.com)