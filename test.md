[테스트 요청] NHN Cloud 자동 구축 툴

1. 다운로드: git clone https://github.com/MyosoonHwang/Py-Cloud-Builder.git
2. 설치: pip install -r requirements.txt
3. 설정: 폴더 안에 .env 파일 만들고 아래 내용 넣기
   NHN_ID=본인아이디
   NHN_PW=API비밀번호
4. 실행: 
   터미널1: py -m webssh.main --port=8888
   터미널2: py web.py