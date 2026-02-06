from pywebio.output import put_html
from pywebio.session import set_env

def apply_styles():
    """공통 CSS 및 폰트 적용"""
    set_env(title='NHN Cloud Manager', output_max_width='1200px')
    
    put_html("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        :root {
            --primary: #344CB7;       /* 딥 블루 */
            --secondary: #577BC1;     /* 라이트 블루 */
            --accent: #FFEB00;        /* 옐로우 포인트 */
            --bg: #F0F4F8;           /* 배경색 */
            --text: #2D3748;
            --white: #FFFFFF;
        }

        body { 
            font-family: 'Pretendard', sans-serif; 
            background-color: var(--bg); 
            color: var(--text);
            margin: 0;
        }

        .card-box { 
            background: var(--white); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }

        .app-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 20px rgba(52, 76, 183, 0.2);
            display: flex; justify-content: space-between; align-items: center;
        }
        .app-header h1 { margin: 0; font-size: 28px; font-weight: 800; }
        .app-header p { margin: 5px 0 0; opacity: 0.8; font-size: 14px; }

        button.btn { border-radius: 12px !important; font-weight: 600 !important; padding: 10px 20px !important; }
        .btn-primary { background-color: var(--primary) !important; border: none; }
        
        .form-control { 
            border-radius: 12px !important; 
            padding: 12px !important; 
            border: 2px solid #E2E8F0 !important;
            transition: all 0.3s;
        }
        
        /* [추가됨] 드롭다운(Select) 박스 높이 및 여백 강제 조정 */
        select.form-control {
            height: 50px !important;       /* 높이 고정 */
            padding-top: 10px !important;  /* 위쪽 여백 */
            padding-bottom: 10px !important; /* 아래쪽 여백 */
            display: flex;                 /* 정렬 보정 */
            align-items: center;
        }
        .form-control:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(52, 76, 183, 0.1) !important; }

        .webio-table { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
        .webio-table th { background-color: #F7FAFC !important; color: #718096; font-weight: 700; padding: 16px !important; }
        .webio-table td { padding: 16px !important; border-bottom: 1px solid #EDF2F7; }
        
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .action-card { cursor: pointer; border: 2px solid transparent; }
        .action-card:hover { transform: translateY(-5px); border-color: var(--primary); }
        .icon-box { font-size: 40px; margin-bottom: 15px; }
    </style>
    """)

def put_header(tid):
    """공통 헤더 출력"""
    put_html(f"""
    <div class="app-header">
        <div>
            <h1>☁️ Dashboard</h1>
            <p>Welcome back! (Tenant ID: {tid})</p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 12px;">Active Session</span>
        </div>
    </div>
    """)