import sys
import getpass
import time
import ipaddress

# 모듈 import
import config
from auth import get_tenant_id_hybrid, get_scoped_token
from utils import validate_cidr
from network_api import fetch_vpcs, fetch_subnets, create_vpc_api, create_subnet_api

# ==========================================
# 리소스 조회 (UI Logic)
# ==========================================
def list_resources_ui(token, my_tenant_id):
    print("\n" + "="*50)
    print("📊 현재 보유 리소스 목록 (My VPCs Only)")
    print("="*50)
    
    vpcs = fetch_vpcs(token)
    subnets = fetch_subnets(token)

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
# 리소스 생성 워크플로우 (UI + Logic)
# ==========================================
def create_workflow_ui(token, my_tenant_id):
    print("\n🏗️  [새 VPC 생성]")
    
    # 1. 기존 데이터 가져오기 (중복 체크용)
    existing_vpcs = fetch_vpcs(token)
    existing_subnets = fetch_subnets(token)

    existing_vpc_names = {v['name'] for v in existing_vpcs if v.get('tenant_id') == my_tenant_id}
    existing_subnet_names = {s['name'] for s in existing_subnets if s.get('tenant_id') == my_tenant_id}

    # 2. VPC 이름 입력
    while True:
        vpc_name = input("VPC 이름: ")
        if vpc_name in existing_vpc_names:
            print(f"   ❌ 오류: '{vpc_name}'은(는) 이미 존재하는 VPC 이름입니다.")
            if input("   그래도 만드시겠습니까? (y/n): ").lower() != 'y': continue
        break

    # 3. VPC CIDR 입력
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

    # 4. 서브넷 입력
    subnets_to_create = []
    print("\n📂 서브넷 추가 (종료: q)")
    while True:
        sn = input("   > 이름: ")
        if sn == 'q': break
        
        is_duplicate = False
        if sn in existing_subnet_names:
            print(f"   ❌ 오류: '{sn}'은(는) 이미 사용 중인 이름입니다!")
            is_duplicate = True
            
        if any(s[0] == sn for s in subnets_to_create):
            print(f"   ❌ 오류: 방금 추가한 목록에 '{sn}'이 이미 있습니다!")
            is_duplicate = True
            
        if is_duplicate: continue

        while True:
            sc = input(f"   > [{sn}] CIDR: ")
            if validate_cidr(sc, vpc_cidr):
                subnets_to_create.append((sn, sc))
                break

    if input("\n🚀 생성하시겠습니까? (y/n): ").lower() != 'y': return

    # 5. API 호출 실행
    print(f"\n[Create] VPC '{vpc_name}'...", end="")
    resp = create_vpc_api(token, vpc_name, vpc_cidr)
    
    if resp.status_code not in [200, 201]:
        print(f" 실패! ({resp.status_code})\n{resp.text}")
        return
    
    vpc_id = resp.json()['vpc']['id']
    print(f" 성공! (ID: {vpc_id})")

    for sn, sc in subnets_to_create:
        print(f"[Create] 서브넷 '{sn}'...", end="")
        resp = create_subnet_api(token, vpc_id, sn, sc)
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
    
    # 1. 아이디/비번 로드
    u = config.NHN_ID
    if u: print(f"1. 아이디: {u} (파일 로드)")
    else: u = input("1. 아이디: ")

    p = config.NHN_PW
    if p: print(f"2. 비밀번호: {'*' * 5} (파일 로드)")
    else: p = getpass.getpass("2. 비밀번호: ")

    # 2. Tenant ID 로드
    tid = config.NHN_TENANT_ID
    if tid:
        print(f"👉 Tenant ID: {tid} (파일 로드)")
    else:
        tid = get_tenant_id_hybrid(u, p)
        print(f"✅ 사용 Tenant ID: {tid}")

    # 3. 토큰 발급
    token = get_scoped_token(u, p, tid)

    # 4. 메뉴 루프
    while True:
        print("\n" + "-"*30)
        print(" [메인 메뉴]")
        print(" 1. 📊 조회 (List)")
        print(" 2. 🏗️ 생성 (Create)")
        print(" 0. ❌ 종료")
        print("-"*30)
        
        sel = input("선택 > ")
        if sel == "1": list_resources_ui(token, tid)
        elif sel == "2": create_workflow_ui(token, tid)
        elif sel == "0": sys.exit(0)
        else: print("잘못된 입력")