from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_js, set_env
import time
import requests
import paramiko
import io
import os

# 커스텀 모듈
import network_api
from utils import validate_cidr
import web_style

# ==========================================
# 🧭 공통 네비게이션
# ==========================================
# [수정됨] show_back 옵션 추가 (입력 폼이 있는 페이지에선 버튼 숨김)
def render_navbar(token, tid, title, show_back=True):
    web_style.apply_styles()
    
    # 왼쪽 콘텐츠 결정 (버튼 또는 빈 공간)
    if show_back:
        left_content = put_button("← 뒤로", onclick=lambda: go_back_dashboard(token, tid), color='secondary', outline=True)\
                       .style("width: auto; min-width: 80px; white-space: nowrap; padding: 5px 10px; font-size: 14px;")
    else:
        left_content = put_scope('dummy_left').style("width: 80px;")

    put_row([
        left_content,
        put_markdown(f"## {title}").style("margin: 0; text-align: center; width: 100%;"),
        put_scope('dummy_right').style("width: 80px;")
    ], size='100px auto 100px').style("align-items: center; margin-bottom: 20px;")

def go_back_dashboard(token, tid):
    clear()
    page_dashboard(token, tid)

# ==========================================
# 1. 대시보드 페이지
# ==========================================
def page_dashboard(token, tid):
    clear()
    web_style.apply_styles()
    web_style.put_header(tid)
    
    put_markdown("### ⚡ 바로가기")
    put_html('<div class="dashboard-grid">')
    
    cards = [
        ("📊", "리소스 조회", "VPC/Subnet 목록", 'btn-list'),
        ("🏗️", "VPC 생성", "독립 네트워크 생성", 'btn-create-vpc'),
        ("📂", "서브넷 추가", "네트워크 대역 할당", 'btn-create-subnet'),
        ("🛡️", "Bastion 접속", "SSH 보안 접속 & FIP", 'btn-bastion'),
    ]
    
    for icon, title, desc, btn_id in cards:
        put_html(f"""
        <div class="card-box action-card" onclick="document.getElementById('{btn_id}').click()">
            <div class="icon-box">{icon}</div>
            <h3>{title}</h3>
            <p style="color:#718096;">{desc}</p>
        </div>
        """)
    put_html('</div>')

    put_buttons(
        [
            {'label': '조회', 'value': 'list'},
            {'label': 'VPC 생성', 'value': 'vpc'},
            {'label': '서브넷 추가', 'value': 'subnet'},
            {'label': 'Bastion', 'value': 'bastion'},
        ], 
        onclick=[
            lambda: page_list_resources(token, tid),
            lambda: page_create_vpc(token, tid),
            lambda: page_create_subnet(token, tid),
            lambda: page_bastion_setup(token, tid)
        ]
    ).style('display: none;')
    
    run_js("""
        $('button:contains("조회")').attr('id', 'btn-list');
        $('button:contains("VPC 생성")').attr('id', 'btn-create-vpc');
        $('button:contains("서브넷 추가")').attr('id', 'btn-create-subnet');
        $('button:contains("Bastion")').attr('id', 'btn-bastion');
    """)

    put_html("<br>")
    put_button("로그아웃", onclick=lambda: run_js('location.reload()'), color='danger', outline=True).style("float: right;")

# ==========================================
# 2. 리소스 조회 페이지 (Blocking 없음 -> 뒤로가기 버튼 표시 O)
# ==========================================
def page_list_resources(token, tid):
    clear()
    render_navbar(token, tid, "VPC & Subnet 목록", show_back=True)
    
    put_html('<div class="card-box">')
    
    with put_loading():
        vpcs = network_api.fetch_vpcs(token)
        subnets = network_api.fetch_subnets(token)
    
    my_vpcs = [v for v in vpcs if v['tenant_id'] == tid and v['name'] != "Public Network"]
    
    if not my_vpcs:
        put_warning("표시할 리소스가 없습니다.")
    else:
        table_data = []
        for v in my_vpcs:
            v_subnets = [f"{s['name']} <span style='color:#718096;'>({s['cidr']})</span>" 
                         for s in subnets if s['vpc_id'] == v['id']]
            subnet_html = "<br>".join(v_subnets) if v_subnets else "-"
            
            table_data.append([
                put_html(f"<b>{v['name']}</b>"), 
                v.get('cidrv4', v.get('cidr')), 
                put_html(subnet_html),
                put_html(f"<small>{v['id']}</small>")
            ])
            
        put_table(table_data, header=['VPC Name', 'CIDR', 'Subnets', 'ID'])
    
    put_html('</div>')
    put_button("메인으로 돌아가기", onclick=lambda: go_back_dashboard(token, tid), color='light').style("width: 100%; margin-top: 20px;")

# ==========================================
# 3. VPC 생성 페이지 (입력 Blocking -> 뒤로가기 버튼 숨김 X)
# ==========================================
def page_create_vpc(token, tid):
    clear()
    # [수정] show_back=False : 상단 버튼 숨김 (하단 Cancel 사용 유도)
    render_navbar(token, tid, "VPC 생성", show_back=False)
    
    put_html('<div class="card-box">')
    put_info("💡 취소하려면 하단의 [Cancel] 버튼을 누르세요.")
    
    data = input_group("VPC 설정", [
        input("이름", name='name', placeholder="예: prod-vpc"),
        input("CIDR", name='cidr', placeholder="예: 10.0.0.0/16", value="10.0.0.0/16")
    ], cancelable=True)

    # Cancel 버튼 누르면 여기로 옴 (깔끔하게 뒤로가기)
    if data is None:
        go_back_dashboard(token, tid)
        return
    
    if not validate_cidr(data['cidr']):
        toast("❌ CIDR 형식이 유효하지 않습니다.", color='error')
        time.sleep(1)
        page_create_vpc(token, tid)
        return

    with put_loading():
        resp = network_api.create_vpc_api(token, data['name'], data['cidr'])
    put_html('</div>')

    if resp.status_code in [200, 201]:
        popup("성공 🎉", [
            put_text(f"VPC '{data['name']}' 생성 완료!"),
            put_buttons(['확인'], onclick=lambda _: [close_popup(), go_back_dashboard(token, tid)])
        ])
    else:
        popup("실패 ⚠️", [
            put_text(f"{resp.text}"), 
            put_buttons(['재시도'], onclick=lambda _: [close_popup(), page_create_vpc(token, tid)])
        ])

# ==========================================
# 4. 서브넷 생성 페이지 (입력 Blocking -> 뒤로가기 버튼 숨김 X)
# ==========================================
def page_create_subnet(token, tid):
    clear()
    render_navbar(token, tid, "서브넷 추가", show_back=False)
    
    put_html('<div class="card-box">')
    put_info("💡 취소하려면 하단의 [Cancel] 버튼을 누르세요.")
    
    with put_loading():
        vpcs = network_api.fetch_vpcs(token)
    
    my_vpcs = [v for v in vpcs if v['tenant_id'] == tid and v['name'] != "Public Network"]
    
    if not my_vpcs:
        toast("VPC가 없습니다.", color='error')
        go_back_dashboard(token, tid)
        return

    vpc_options = [{'label': f"{v['name']} ({v.get('cidrv4')})", 'value': v['id']} for v in my_vpcs]
    vpc_dict = {v['id']: v.get('cidrv4') for v in my_vpcs}
    
    def check_form(data):
        parent_cidr = vpc_dict[data['vpc_id']]
        if not validate_cidr(data['cidr'], parent_cidr):
            return ('cidr', f"⛔ 범위 오류: '{data['cidr']}'은 VPC({parent_cidr}) 범위를 벗어납니다.")
        if not data['name'].strip():
             return ('name', "이름을 입력해주세요.")
        return None

    data = input_group("서브넷 설정", [
        select("대상 VPC", options=vpc_options, name='vpc_id'),
        input("서브넷 이름", name='name', placeholder="예: web-sub-01"),
        input("서브넷 CIDR", name='cidr', placeholder="예: 10.0.1.0/24")
    ], validate=check_form, cancelable=True)
    
    if data is None: 
        go_back_dashboard(token, tid)
        return
    
    with put_loading():
        resp = network_api.create_subnet_api(token, data['vpc_id'], data['name'], data['cidr'])
    put_html('</div>')

    if resp.status_code in [200, 201]:
        popup("성공 🎉", [
            put_text("서브넷 추가 완료!"), 
            put_buttons(['확인'], onclick=lambda _: [close_popup(), go_back_dashboard(token, tid)])
        ])
    else:
        popup("실패 ⚠️", [
            put_text(f"{resp.text}"), 
            put_button("재시도", onclick=lambda _: [close_popup(), page_create_subnet(token, tid)])
        ])

# ==========================================
# 5. Bastion 자동화 페이지 (입력 Blocking -> 뒤로가기 버튼 숨김 X)
# ==========================================
def page_bastion_setup(token, tid):
    clear()
    render_navbar(token, tid, "Bastion 서버 연결", show_back=False)
    
    put_html('<div class="card-box">')
    put_info("💡 취소하려면 하단의 [Cancel] 버튼을 누르세요.")

    # 인스턴스 포트 조회
    with put_loading():
        ports = network_api.fetch_ports(token)
    
    compute_ports = [p for p in ports if p['tenant_id'] == tid and p['device_owner'].startswith('compute:')]
    
    if not compute_ports:
        put_error("생성된 인스턴스가 없습니다.")
        put_button("돌아가기", onclick=lambda: go_back_dashboard(token, tid))
        return

    port_options = [{'label': f"IP: {p['fixed_ips'][0]['ip_address']} ({p['id'][:8]}...)", 'value': p['id']} for p in compute_ports]
    
    data = input_group("연결 정보 입력", [
        select("대상 서버", options=port_options, name='port_id'),
        file_upload("SSH Key (.pem)", name='key_file', accept='.pem,.key'),
        input("User", name='username', value='ubuntu', placeholder="Ubuntu: ubuntu, CentOS: centos"),
        input("Public Net ID", name='pub_id', value='4b61db01-8183-4540-b2a3-47254a58298d', readonly=True)
    ], cancelable=True)

    if data is None: 
        go_back_dashboard(token, tid)
        return

    # 자동화 로직 수행
    put_markdown("---")
    put_text("⚙️ 네트워크 자동 설정 중...")
    
    try:
        # 1. 내 IP 조회
        try:
            my_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            my_ip = "0.0.0.0" # IP 조회 실패 시 예외 처리
        put_text(f"✅ Client IP: {my_ip}")

        # 2. 보안그룹 처리
        sg_name = "auto-bastion-sg"
        sgs = network_api.fetch_security_groups(token)
        target_sg = next((sg for sg in sgs if sg['name'] == sg_name), None)
        
        if not target_sg:
            resp_sg = network_api.create_security_group(token, sg_name, "Auto Bastion SG")
            if resp_sg.status_code in [200, 201]:
                target_sg_id = resp_sg.json()['security_group']['id']
                network_api.create_security_group_rule(token, target_sg_id, "tcp", 22, f"{my_ip}/32")
                put_text("✅ 보안 그룹 생성 완료")
            else:
                put_text("⚠️ 보안 그룹 생성 실패 (기존 그룹 사용 시도)")
        else:
            put_text("✅ 기존 보안 그룹 확인")

        # 3. Floating IP 처리 (여기가 에러 났던 부분!)
        fips = network_api.fetch_floating_ips(token)
        target_port_id = data['port_id']
        
        # [수정됨] .get('port_id')를 사용하여 에러 방지
        my_fip = next((f for f in fips if f.get('port_id') == target_port_id), None)
        
        if my_fip:
            final_ip = my_fip['floating_ip_address']
        else:
            # 남는 FIP 찾기 (port_id가 None이거나 없는 것)
            free_fip = next((f for f in fips if f.get('port_id') is None), None)
            
            if free_fip:
                network_api.associate_floating_ip(token, free_fip['id'], target_port_id)
                final_ip = free_fip['floating_ip_address']
            else:
                # 생성 후 연결
                resp_fip = network_api.create_floating_ip(token, data['pub_id'])
                if resp_fip.status_code not in [200, 201]:
                    raise Exception(f"Floating IP 생성 실패: {resp_fip.text}")
                    
                new_fip = resp_fip.json()['floatingip']
                network_api.associate_floating_ip(token, new_fip['id'], target_port_id)
                final_ip = new_fip['floating_ip_address']
        
        put_text(f"✅ 접속 IP 확보: {final_ip}")
        put_success("🚀 연결 준비 완료! 콘솔을 실행합니다...")
        time.sleep(1)
        
        # SSH 콘솔 실행
        run_ssh_console(token, tid, final_ip, data['username'], data['key_file']['content'])

    except Exception as e:
        put_error(f"Error: {e}")
        put_button("돌아가기", onclick=lambda: go_back_dashboard(token, tid))

# ==========================================
# 6. 진짜 웹 터미널 (WebSSH Embed)
# ==========================================
def run_ssh_console(token, tid, hostname, username, key_data):
    clear()
    # [수정] 여기도 입력이 없지만 터미널 화면이므로 상단 버튼 숨김 (아래 종료 버튼 사용 유도)
    render_navbar(token, tid, f"SSH: {username}@{hostname}", show_back=False)
    
    key_filename = f"key_{hostname}.pem"
    try:
        with open(key_filename, "wb") as f:
            f.write(key_data)
        print(f"🔑 Key saved at: {os.path.abspath(key_filename)}")
    except Exception as e:
        toast(f"키 저장 실패: {e}", color='error')

    put_html(f"""
    <div class="card-box" style="margin-bottom: 20px; padding: 20px; background: #EBF8FF; border: 1px solid #BEE3F8;">
        <h3 style="margin-top: 0; color: #2B6CB0;">🚀 접속 정보</h3>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div><b>Host:</b> <code style="background:white; padding:5px;">{hostname}</code></div>
            <div><b>Port:</b> <code style="background:white; padding:5px;">22</code></div>
            <div><b>Username:</b> <code style="background:white; padding:5px;">{username}</code></div>
        </div>
        <hr style="border: 0; border-top: 1px solid #BEE3F8; margin: 10px 0;">
        <p style="margin: 0; font-size: 14px; color: #4A5568;">
            💡 아래 터미널의 <b>Private Key</b> 칸을 클릭하고, 다운로드한 <b>{key_filename}</b> 파일을 선택하세요.
        </p>
    </div>
    """)
    
    with open(key_filename, "rb") as f:
        content = f.read()
    
    put_row([
        put_file(key_filename, content, f"🔑 {key_filename} 다운로드 (클릭)"),
        put_text("👈 이 파일을 받아서 아래에 넣으세요").style("display:flex; align-items:center; color: #718096; margin-left: 10px;")
    ]).style("margin-bottom: 20px;")

    put_html("""
    <iframe src="http://127.0.0.1:8888" 
            style="width: 100%; height: 600px; border: none; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
    </iframe>
    """)
    
    put_html("<br>")
    put_button("작업 종료 및 돌아가기", onclick=lambda: go_back_dashboard(token, tid), color='danger', outline=True)