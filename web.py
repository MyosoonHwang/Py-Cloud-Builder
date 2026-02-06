# web.py 전체 덮어쓰기

from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
import time
import subprocess
import sys
import threading

# 모듈 가져오기
import config
import auth
import web_style
import web_pages 

def run_webssh_server():
    """백그라운드에서 WebSSH 서버 실행 (포트 8888)"""
    try:
        print("🚀 [System] WebSSH 서버를 시작합니다 (Port: 8888)...")
        # [수정됨] 로그를 숨기지 않고 터미널에 출력하도록 변경 (에러 확인용)
        proc = subprocess.Popen(
            [sys.executable, "-m", "webssh.main", "--port=8888", "--fbidhttp=False"],
            shell=False
        )
        proc.wait() # 프로세스가 종료될 때까지 대기
    except Exception as e:
        print(f"❌ [Error] WebSSH 서버 실행 실패: {e}")

def main():
    clear()
    web_style.apply_styles() 
    
    # 로그인 화면
    put_html("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div class="card-box" style="width: 400px; text-align: center; padding: 50px;">
            <div style="font-size: 60px; margin-bottom: 20px;">☁️</div>
            <h2 style="color: #344CB7; margin-bottom: 10px;">NHN Cloud Manager</h2>
            <p style="color: #718096; margin-bottom: 40px;">Secure & Simple Resource Builder</p>
            <div id="login-area"></div>
        </div>
    </div>
    """)
    
    with use_scope('login-area'):
        data = input_group("", [
            input("아이디", name='id', placeholder="Email", value=config.NHN_ID or ""),
            input("비밀번호", name='pw', type=PASSWORD, placeholder="Password", value=config.NHN_PW or "")
        ])
    
    try:
        tid = config.NHN_TENANT_ID
        if not tid:
            with put_loading(shape='border', color='primary'):
                tid = auth.get_tenant_id_hybrid(data['id'], data['pw'])
            
        with put_loading(shape='border', color='primary'):
            token = auth.get_scoped_token(data['id'], data['pw'], tid)
        
        toast("로그인 성공!", color='success')
        time.sleep(0.5)
        
        web_pages.page_dashboard(token, tid)
        
    except Exception as e:
        put_error(f"로그인 실패: {e}")
        time.sleep(2)
        main()

if __name__ == '__main__':
    # WebSSH 서버를 별도 스레드로 실행
    t = threading.Thread(target=run_webssh_server, daemon=True)
    t.start()
    
    # 메인 서버 실행 (8081 포트)
    start_server(main, port=8081, debug=True, auto_open_webbrowser=True)