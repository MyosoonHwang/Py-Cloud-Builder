import requests
import sys
from config import IDENTITY_URL

def get_tenant_id_hybrid(username, password):
    print(f"\n[🔍 프로젝트 검색] 자동 조회를 시도합니다...", end="")
    try:
        url = f"{IDENTITY_URL}/tokens"
        headers = {'Content-Type': 'application/json'}
        body = { "auth": { "passwordCredentials": { "username": username, "password": password } } }
        
        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()
        unscoped_token = resp.json()['access']['token']['id']
        
        headers['X-Auth-Token'] = unscoped_token
        resp_tenants = requests.get(f"{IDENTITY_URL}/tenants", headers=headers)
        resp_tenants.raise_for_status()
        
        tenants = resp_tenants.json()['tenants']
        print(" 성공! ✅")
        
        if not tenants:
            print("   (접근 가능한 프로젝트가 없습니다)")
            raise Exception("No Tenants")

        if len(tenants) == 1:
            t = tenants[0]
            print(f"👉 자동 선택: '{t['name']}' ({t['id']})")
            return t['id']
        else:
            print("\n[📂 프로젝트 선택]")
            for i, t in enumerate(tenants):
                print(f"  {i+1}. {t['name']} ({t['id']})")
            while True:
                sel = input("\n번호 선택: ")
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(tenants): return tenants[idx]['id']
                except: pass

    except Exception:
        print(" 실패")
        print("⚠️  자동 조회 실패. Tenant ID를 직접 입력해주세요.")
        while True:
            manual_id = input("\n👉 Tenant ID 입력: ").strip()
            if manual_id: return manual_id

def get_scoped_token(username, password, tenant_id):
    url = f"{IDENTITY_URL}/tokens"
    headers = {'Content-Type': 'application/json'}
    body = { "auth": { "tenantId": tenant_id, "passwordCredentials": { "username": username, "password": password } } }
    try:
        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()['access']['token']['id']
    except Exception as e:
        print(f"\n❌ 인증 실패: {e}")
        sys.exit(1)