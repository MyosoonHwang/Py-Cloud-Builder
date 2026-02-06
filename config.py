import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API URL 설정
IDENTITY_URL = "https://api-identity-infrastructure.nhncloudservice.com/v2.0"
NETWORK_API_URL = "https://kr1-api-network-infrastructure.nhncloudservice.com"

# 환경 변수 가져오기
NHN_ID = os.getenv("NHN_ID")
NHN_PW = os.getenv("NHN_PW")
NHN_TENANT_ID = os.getenv("NHN_TENANT_ID")