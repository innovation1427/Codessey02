import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import os

# --- 1. 발송자 정보 설정 ---
sender_email = "innovation1426@gmail.com"
password = "fdfhpgprrufiwtpy"

# --- 2. CSV에서 전체 수신자 목록 가져오기 ---
receiver_list = []

# CSV 파일 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_filename = "mail_target_list.csv"
csv_path = os.path.join(script_dir, csv_filename)

try:
    # 'csv_path' 변수로 파일 열기
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # 헤더 건너뛰기
        for name, email in reader:
            if email:
                receiver_list.append(email)
    
    if not receiver_list:
        print("CSV 파일에 유효한 이메일 주소가 없습니다.")
        # 프로그램이 더 진행되지 않도록 여기서 종료
        exit() 
        
    print(f"총 {len(receiver_list)}명의 수신자 목록을 읽었습니다.")

    # --- 3. (HTML) 공통 이메일 메시지 생성 ---
    msg = MIMEMultipart()
    msg['Subject'] = Header("[긴급] 화성 생존자 구조 요청 (전체 공지)", "utf-8")
    msg['From'] = sender_email
    msg['To'] = "undisclosed-recipients@example.com" 

    html_body = """
    <html>
    <body>
        <h1>긴급 공지: 화성 생존자 발생</h1>
        <p>본 메일은 NASA, KARI 등 주요 우주 기관 관계자분들께 발송되었습니다.</p>
        <p style="color:red; font-weight:bold;">저는 화성에 고립된 한송희 박사이며, 생존해 있습니다.</p>
        <p>- 한송희 드림 -</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # --- 4. SMTP 서버 접속 및 전체 발송 ---
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, password)
    
    smtp.sendmail(sender_email, receiver_list, msg.as_string())
    
    print(f"{len(receiver_list)}명에게 BCC로 메일을 성공적으로 발송했습니다.")

except smtplib.SMTPAuthenticationError:
    print("로그인 실패: 이메일 주소 또는 앱 비밀번호를 확인하세요.")
except FileNotFoundError:
    print(f"CSV 파일({csv_path})을 찾을 수 없습니다.")
except Exception as e:
    print(f"메일 발송 중 오류가 발생했습니다: {e}")

finally:
    if 'smtp' in locals() and smtp.sock:
        smtp.quit()
        print("SMTP 연결을 종료했습니다.")
