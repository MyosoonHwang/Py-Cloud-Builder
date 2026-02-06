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
# ⚙️ 설정 및 상수 (하드코딩 제거)
# ==========================================
PUBLIC_NET_ID = '4b61db01-8183-4540-b2a3-47254a58298d'
DEFAULT_CIDR = '10.0.0.0/16'

# ==========================================
# 🛠️ 헬퍼 함수 (중복 제거용)
# ==========================================
def go_back(token, tid):
    """대시보드로 돌아가기"""
    clear()
    page_dashboard(token, tid)

def handle_api_result(response, success_msg, token, tid, retry_func=None):
    """API 결과에 따라 성공/실패 팝업을 띄워주는 공통 함수"""
    put_html('</div>') # 카드 박스 닫기
    
    if response.status_code in [200, 201]:
        popup("성공 🎉", [
            put_text(success_msg),
            put_buttons(['확인'], onclick=lambda _: [close_popup(), go_back(token, tid)])
        ])
    else:
        buttons = [{'label': '확인', 'value': 'ok'}]
        if retry_func:
            buttons.append({'label': '재시도', 'value': 'retry'})
            
        def on_fail(choice):
            close_popup()
            if choice == 'retry': retry_func(token, tid)
            else: go_back(token, tid)

        popup("실패 ⚠️", [
            put_text(f"오류 내용: {response.text}"),
            put_buttons(buttons, onclick=on_fail)
        ])

def render_navbar(token, tid, title, show_back=True):
    """상단 네비게이션 바 렌더링"""
    web_style.apply_styles()
    
    if show_back:
        left_btn = put_button("← 뒤로", onclick=lambda: go_back(token, tid), color='secondary', outline=True)\
                   .style("width: auto; padding: 5px 10px; font-size: 14px;")
    else:
        left_btn = put_scope('dummy_left').style("width: 80px;")

    put_row([
        left_btn,
        put_markdown(f"## {title}").style("margin: 0; text-align: center; width: 100%;"),
        put_scope('dummy_right').style("width: 80px;")
    ], size='100px auto 100px').style("align-items: center; margin-bottom: 20px;")

# ==========================================
# 1. 대시보드 페이지
# ==========================================
def page_dashboard(token, tid):
    clear()
    web_style.apply_styles()
    web_style.put_header(tid)
    
    put_markdown("### ⚡ 바로가기")
    
    # 카드 메뉴 데이터
    menu_items = [
        ("📊", "리소스 조회", "VPC/Subnet 목록", 'btn-list', lambda: page_list_resources(token, tid)),
        ("🏗️", "VPC 생성", "독립 네트워크 생성", 'btn-vpc', lambda: page_create_vpc(token, tid)),
        ("📂", "서브넷 추가", "네트워크 대역 할당", 'btn-subnet', lambda: page_create_subnet(token, tid)),
        ("🛡️", "Bastion 접속", "SSH 보안 접속 & FIP", 'btn-bastion', lambda: page_bastion_setup(token, tid)),
    ]
    
    put_html('<div class="dashboard-grid">')
    for icon, title, desc, btn_id, _ in menu_items:
        put_html(f"""
        <div class="card-box action-card" onclick="document.getElementById('{btn_id}').click()">
            <div class="icon-box">{icon}</div>
            <h3>{title}</h3>
            <p style="color:#718096;">{desc}</p>
        </div>
        """)
    put_html('</div>')

    # 숨겨진 버튼 생성 (이벤트 연결용)
    buttons = [{'label': m[1], 'value': m[3]} for m in menu_items]
    callbacks = [m[4] for m in menu_items]
    
    put_buttons(buttons, onclick=callbacks).style('display: none;')
    
    # JS로 ID 매핑
    js_code = "".join([f"$('button:contains(\"{m[1]}\")').attr('id', '{m[3]}');" for m in menu_items])
    run_js(js_code)

    put_html("<br>")
    put_button("로그아웃", onclick=lambda: run_js('location.reload()'), color='danger', outline=True).style("float: right;")

# ==========================================
# 2. 리소스 조회 페이지
# ==========================================
def page_list_resources(token, tid):
    clear()
    render_navbar(token, tid, "VPC & Subnet 목록")
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
            
            table_data.append([
                put_html(f"<b>{v['name']}</b>"), 
                v.get('cidrv4', v.get('cidr')), 
                put_html("<br>".join(v_subnets) if v_subnets else "-"),
                put_html(f"<small>{v['id']}</small>")
            ])
        put_table(table_data, header=['VPC Name', 'CIDR', 'Subnets', 'ID'])
    
    put_html('</div>')
    put_button("메인으로 돌아가기", onclick=lambda: go_back(token, tid), color='light').style("width: 100%; margin-top: 20px;")

# ==========================================
# 3. VPC 생성 페이지
# ==========================================
def page_create_vpc(token, tid):
    clear()
    render_navbar(token, tid, "VPC 생성", show_back=False)
    put_html('<div class="card-box">')
    put_info("💡 취소하려면 하단의 [Cancel] 버튼을 누르세요.")
    
    data = input_group("VPC 설정", [
        input("이름", name='name', placeholder="예: prod-vpc"),
        input("CIDR", name='cidr', placeholder=f"예: {DEFAULT_CIDR}", value=DEFAULT_CIDR)
    ], cancelable=True)

    if data is None: return go_back(token, tid)
    
    if not validate_cidr(data['cidr']):
        toast("❌ CIDR 형식이 유효하지 않습니다.", color='error')
        time.sleep(1)
        return page_create_vpc(token, tid)

    with put_loading():
        resp = network_api.create_vpc_api(token, data['name'], data['cidr'])
    
    handle_api_result(resp, f"VPC '{data['name']}' 생성 완료!", token, tid, page_create_vpc)

# ==========================================
# 4. 서브넷 생성 페이지
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
        toast("VPC가 없습니다. 먼저 VPC를 생성하세요.", color='error')
        return go_back(token, tid)

    vpc_options = [{'label': f"{v['name']} ({v.get('cidrv4')})", 'value': v['id']} for v in my_vpcs]
    vpc_dict = {v['id']: v.get('cidrv4') for v in my_vpcs}
    
    def check_form(data):
        if not validate_cidr(data['cidr'], vpc_dict[data['vpc_id']]):
            return ('cidr', "⛔ 범위 오류: VPC 범위를 벗어납니다.")
        if not data['name'].strip(): return ('name', "필수 입력입니다.")
        return None

    data = input_group("서브넷 설정", [
        select("대상 VPC", options=vpc_options, name='vpc_id'),
        input("서브넷 이름", name='name', placeholder="예: web-sub-01"),
        input("서브넷 CIDR", name='cidr', placeholder="예: 10.0.1.0/24")
    ], validate=check_form, cancelable=True)
    
    if data is None: return go_back(token, tid)
    
    with put_loading():
        resp = network_api.create_subnet_api(token, data['vpc_id'], data['name'], data['cidr'])
    
    handle_api_result(resp, "서브넷 추가 완료!", token, tid, page_create_subnet)

# ==========================================
# 5. Bastion 자동화 페이지
# ==========================================
def page_bastion_setup(token, tid):
    clear()
    render_navbar(token, tid, "Bastion 서버 연결", show_back=False)
    put_html('<div class="card-box">')
    put_info("💡 취소하려면 하단의 [Cancel] 버튼을 누르세요.")

    with put_loading():
        ports = network_api.fetch_ports(token)
    
    compute_ports = [p for p in ports if p['tenant_id'] == tid and p['device_owner'].startswith('compute:')]
    
    if not compute_ports:
        put_error("생성된 인스턴스가 없습니다.")
        put_button("돌아가기", onclick=lambda: go_back(token, tid))
        return

    port_opts = [{'label': f"IP: {p['fixed_ips'][0]['ip_address']} ({p['id'][:8]}...)", 'value': p['id']} for p in compute_ports]
    
    data = input_group("연결 정보 입력", [
        select("대상 서버", options=port_opts, name='port_id'),
        file_upload("SSH Key (.pem)", name='key_file', accept='.pem,.key'),
        input("User", name='username', value='ubuntu', placeholder="Ubuntu: ubuntu, CentOS: centos"),
        input("Public Net ID", name='pub_id', value=PUBLIC_NET_ID, readonly=True)
    ], cancelable=True)

    if data is None: return go_back(token, tid)

    # 자동화 로직
    put_markdown("---")
    put_text("⚙️ 네트워크 자동 설정 중...")
    
    try:
        # 1. 내 IP
        my_ip = requests.get('https://api.ipify.org').text
        put_text(f"✅ Client IP: {my_ip}")

        # 2. 보안그룹
        sg_name = "auto-bastion-sg"
        sgs = network_api.fetch_security_groups(token)
        if not any(sg['name'] == sg_name for sg in sgs):
            resp = network_api.create_security_group(token, sg_name, "Auto Bastion SG")
            sg_id = resp.json()['security_group']['id']
            network_api.create_security_group_rule(token, sg_id, "tcp", 22, f"{my_ip}/32")
            put_text("✅ 보안 그룹 생성 완료")
        else:
            put_text("✅ 기존 보안 그룹 확인")

        # 3. Floating IP
        fips = network_api.fetch_floating_ips(token)
        target_port = data['port_id']
        
        # FIP 할당 로직
        existing_fip = next((f for f in fips if f['port_id'] == target_port), None)
        unused_fip = next((f for f in fips if f['port_id'] is None), None)

        if existing_fip:
            final_ip = existing_fip['floating_ip_address']
        elif unused_fip:
            network_api.associate_floating_ip(token, unused_fip['id'], target_port)
            final_ip = unused_fip['floating_ip_address']
        else:
            resp = network_api.create_floating_ip(token, data['pub_id'])
            new_fip = resp.json()['floatingip']
            network_api.associate_floating_ip(token, new_fip['id'], target_port)
            final_ip = new_fip['floating_ip_address']
        
        put_text(f"✅ 접속 IP 확보: {final_ip}")
        put_success("🚀 연결 준비 완료! 콘솔을 실행합니다...")
        time.sleep(1)
        
        run_ssh_console(token, tid, final_ip, data['username'], data['key_file']['content'])

    except Exception as e:
        put_error(f"Error: {e}")
        put_button("돌아가기", onclick=lambda: go_back(token, tid))

# ==========================================
# 6. WebSSH 터미널 페이지
# ==========================================
def run_ssh_console(token, tid, hostname, username, key_data):
    clear()
    render_navbar(token, tid, f"SSH: {username}@{hostname}", show_back=False)
    
    # 키 파일 저장
    key_filename = f"key_{hostname}.pem"
    try:
        with open(key_filename, "wb") as f: f.write(key_data)
        print(f"🔑 Key saved: {os.path.abspath(key_filename)}")
    except Exception as e:
        toast(f"키 저장 실패: {e}", color='error')

    # 안내 UI
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
    
    with open(key_filename, "rb") as f: content = f.read()
    
    put_row([
        put_file(key_filename, content, f"🔑 {key_filename} 다운로드 (클릭)"),
        put_text("👈 이 파일을 받아서 아래에 넣으세요").style("display:flex; align-items:center; color: #718096; margin-left: 10px;")
    ]).style("margin-bottom: 20px;")

    # WebSSH iframe (127.0.0.1 사용)
    put_html("""
    <iframe src="http://127.0.0.1:8888" 
            style="width: 100%; height: 600px; border: none; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
    </iframe>
    """)
    
    put_html("<br>")
    put_button("작업 종료 및 돌아가기", onclick=lambda: go_back(token, tid), color='danger', outline=True)