import requests
import json
import getpass
import sys
import ipaddress
import time
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================================
# 0. 설정
# ==========================================
IDENTITY_URL = "https://api-identity-infrastructure.nhncloudservice.com/v2.0"
NETWORK_API_URL = "https://kr1-api-network-infrastructure.nhncloudservice.com"

# ==========================================
# 1. 인증 및 Tenant ID (하이브리드)
# ==========================================
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

# ==========================================
# 2. 리소스 조회 (내 것만 보기)
# ==========================================
def list_resources(token, my_tenant_id):
    print("\n" + "="*50)
    print("📊 현재 보유 리소스 목록 (My VPCs Only)")
    print("="*50)
    headers = {'X-Auth-Token': token}
    
    try:
        vpcs = requests.get(f"{NETWORK_API_URL}/v2.0/vpcs", headers=headers).json().get('vpcs', [])
        subnets = requests.get(f"{NETWORK_API_URL}/v2.0/vpcsubnets", headers=headers).json().get('vpcsubnets', [])
    except Exception as e:
        print(f"❌ 조회 중 오류 발생: {e}")
        return

    count = 0
    for v in vpcs:
        if v.get('tenant_id') != my_tenant_id: continue
        if v.get('name') == "Public Network": continue

        count += 1
        v_name = v.get('name', 'No Name')
        v_cidr = v.get('cidrv4', v.get('cidr', 'N/A'))
        v_id = v['id']
        
        print(f"☁️  VPC: {v_name} ({v_cidr})")
        
        my_subnets = [s for s in subnets if s['vpc_id'] == v_id]
        if not my_subnets:
            print("└── (서브넷 없음)")
        else:
            for i, s in enumerate(my_subnets):
                prefix = "└──" if i == len(my_subnets)-1 else "├──"
                print(f"{prefix} 📂 {s.get('name')} ({s.get('cidr')})")
        print("")

    if count == 0:
        print("   (보유한 VPC가 없습니다)")

# ==========================================
# 3. 리소스 생성 (이름 중복 체크 추가됨)
# ==========================================
def validate_cidr(cidr_text, vpc_cidr=None):
    try:
        subnet_net = ipaddress.IPv4Network(cidr_text)
        if vpc_cidr and not subnet_net.subnet_of(ipaddress.IPv4Network(vpc_cidr)):
            print(f"   ❌ 범위 오류: VPC({vpc_cidr}) 밖입니다.")
            return None
        return str(subnet_net)
    except: return None

def create_workflow(token, my_tenant_id):
    print("\n🏗️  [새 VPC 생성]")
    
    headers = {'X-Auth-Token': token}
    
    # 1. 기존 데이터 가져오기 (이름 중복 체크용)
    try:
        existing_vpcs = requests.get(f"{NETWORK_API_URL}/v2.0/vpcs", headers=headers).json().get('vpcs', [])
        existing_subnets = requests.get(f"{NETWORK_API_URL}/v2.0/vpcsubnets", headers=headers).json().get('vpcsubnets', [])
    except:
        existing_vpcs = []
        existing_subnets = []

    # 내 프로젝트의 기존 이름들 추출 (Set으로 빠르게 검색)
    existing_vpc_names = {v['name'] for v in existing_vpcs if v.get('tenant_id') == my_tenant_id}
    existing_subnet_names = {s['name'] for s in existing_subnets if s.get('tenant_id') == my_tenant_id}

    # 2. VPC 이름 입력 (중복 체크)
    while True:
        vpc_name = input("VPC 이름: ")
        if vpc_name in existing_vpc_names:
            print(f"   ❌ 오류: '{vpc_name}'은(는) 이미 존재하는 VPC 이름입니다.")
            if input("   그래도 만드시겠습니까? (y/n): ").lower() != 'y': continue
        break

    # 3. VPC CIDR 입력 (대역 중복 체크)
    while True:
        vpc_cidr = input("VPC CIDR (예: 10.0.0.0/16): ")
        if not validate_cidr(vpc_cidr):
            print("   ❌ 올바른 형식이 아닙니다.")
            continue
        
        target = ipaddress.IPv4Network(vpc_cidr)
        overlap = False
        for v in existing_vpcs:
            if v.get('tenant_id') != my_tenant_id: continue
            if v.get('name') == "Public Network": continue
            if v.get('cidrv4') == "0.0.0.0/0": continue

            c = v.get('cidrv4', v.get('cidr'))
            if c and target.overlaps(ipaddress.IPv4Network(c)):
                print(f"⚠️  경고: '{v.get('name')}'({c})와 겹칩니다!")
                overlap = True
        
        if not overlap:
            print("✅ 사용 가능한 쾌적한 대역입니다.")
            break
        
        if input("   그래도 진행합니까? (y/n): ").lower() == 'y': break

    # 4. 서브넷 입력 (이름 중복 체크 적용)
    subnets = []
    print("\n📂 서브넷 추가 (종료: q)")
    while True:
        sn = input("   > 이름: ")
        if sn == 'q': break
        
        # [NEW] 서브넷 이름 중복 체크
        is_duplicate = False
        
        # 1) 기존에 있는 것과 겹치는지?
        if sn in existing_subnet_names:
            print(f"   ❌ 오류: '{sn}'은(는) 이미 사용 중인 이름입니다!")
            is_duplicate = True
            
        # 2) 방금 입력한 목록에 있는지?
        if any(s[0] == sn for s in subnets):
            print(f"   ❌ 오류: 방금 추가한 목록에 '{sn}'이 이미 있습니다!")
            is_duplicate = True
            
        if is_duplicate:
            continue

        while True:
            sc = input(f"   > [{sn}] CIDR: ")
            if validate_cidr(sc, vpc_cidr):
                subnets.append((sn, sc))
                break

    if input("\n🚀 생성하시겠습니까? (y/n): ").lower() != 'y': return

    # 5. 실행
    print(f"\n[Create] VPC '{vpc_name}'...", end="")
    body = { "vpc": { "name": vpc_name, "cidrv4": vpc_cidr } }
    resp = requests.post(f"{NETWORK_API_URL}/v2.0/vpcs", json=body, headers={'X-Auth-Token': token, 'Content-Type': 'application/json'})
    
    if resp.status_code not in [200, 201]:
        print(f" 실패! ({resp.status_code})\n{resp.text}")
        return
    
    vpc_id = resp.json()['vpc']['id']
    print(f" 성공! (ID: {vpc_id})")

    for sn, sc in subnets:
        print(f"[Create] 서브넷 '{sn}'...", end="")
        body = { "vpcsubnet": { "vpc_id": vpc_id, "cidr": sc, "name": sn } }
        resp = requests.post(f"{NETWORK_API_URL}/v2.0/vpcsubnets", json=body, headers={'X-Auth-Token': token, 'Content-Type': 'application/json'})
        if resp.status_code in [200, 201]: print(" 성공! ✅")
        else: print(f" 실패!")
        time.sleep(0.5)

# ==========================================
# 메인 실행
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      🔐 NHN Cloud Manager (.env Supported)")
    print("="*50)
    
    # 1. 아이디 로드 (파일에 있으면 그거 쓰고, 없으면 물어봄)
    u = os.getenv("NHN_ID")
    if u:
        print(f"1. 아이디: {u} (파일에서 자동 입력됨)")
    else:
        u = input("1. 아이디: ")

    # 2. 비밀번호 로드
    p = os.getenv("NHN_PW")
    if p:
        print(f"2. 비밀번호: {'*' * 5} (파일에서 자동 입력됨)")
    else:
        p = getpass.getpass("2. 비밀번호: ")

    # 3. Tenant ID 로드 (파일에 있으면 그거 쓰고, 없으면 자동 조회 기능 실행)
    env_tid = os.getenv("NHN_TENANT_ID")
    
    if env_tid:
        print(f"👉 Tenant ID: {env_tid} (파일에서 자동 입력됨)")
        tid = env_tid
    else:
        # 파일에 없으면 기존처럼 자동 조회 기능 사용
        tid = get_tenant_id_hybrid(u, p)
        print(f"✅ 사용 Tenant ID: {tid}")

    # 4. 토큰 발급 및 메뉴 실행 (기존과 동일)
    token = get_scoped_token(u, p, tid)

    while True:
        print("\n" + "-"*30)
        print(" [메인 메뉴]")
        print(" 1. 📊 조회 (List)")
        print(" 2. 🏗️ 생성 (Create)")
        print(" 0. ❌ 종료")
        print("-"*30)
        
        sel = input("선택 > ")
        if sel == "1": list_resources(token, tid)
        elif sel == "2": create_workflow(token, tid)
        elif sel == "0": sys.exit(0)
        else: print("잘못된 입력")