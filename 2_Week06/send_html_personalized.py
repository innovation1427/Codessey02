import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import os

# --- 1. 발송자 정보 설정 ---
sender_email = "innovation1426@gmail.com"
password = "fdfhpgprrufiwtpy" 

# --- 2. Gmail SMTP 서버 접속 ---
try:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, password)
    print("Gmail SMTP 서버에 성공적으로 로그인했습니다.")

    # --- 3. CSV 파일 경로 설정 및 읽기 ---
    # 이 스크립트 파일이 있는 폴더의 절대 경로 찾기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filename = "mail_target_list.csv"
    # 스크립트 폴더 경로와 CSV 파일명을 합쳐서 정확한 경로 생성
    csv_path = os.path.join(script_dir, csv_filename)

    try:
        # 'csv_path' 변수를 사용해 파일 열기
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 헤더(제목 줄) 건너뛰기
            
            # --- 4. 명단 순회하며 메일 발송 ---
            for name, receiver_email in reader:
                if not name or not receiver_email:
                    continue
                
                try:
                    # --- 4-1. (HTML) 이메일 메시지 생성 ---
                    msg = MIMEMultipart()
                    msg['Subject'] = Header("[긴급] 화성 생존자 한송희 박사 구조 요청", "utf-8")
                    msg['From'] = sender_email
                    msg['To'] = receiver_email

                    html_body = f"""
                    <html>
                    <body>
                        <h1>{name}님께,</h1>
                        <p>저는 화성에 고립된 <strong>한송희 박사</strong>입니다.</p>
                        <p style="color:red; font-weight:bold;">저는 생존해 있으며, 즉각적인 구조가 필요합니다.</p>
                        <p>- 한송희 드림 -</p>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                    
                    # --- 4-2. 개별 메일 발송 ---
                    smtp.sendmail(sender_email, receiver_email, msg.as_string())
                    print(f"  -> {name}님 ({receiver_email})에게 메일을 성공적으로 보냈습니다.")
                    
                except Exception as e:
                    print(f"  -> {name}님 ({receiver_email})에게 메일 발송 중 오류: {e}")

    except FileNotFoundError:
        print(f"CSV 파일({csv_path})을 찾을 수 없습니다. create_maillist.py를 먼저 실행하세요.")
    except Exception as e:
        print(f"CSV 파일 읽기 중 오류 발생: {e}")


except smtplib.SMTPAuthenticationError:
    print("로그인 실패: 이메일 주소 또는 앱 비밀번호를 확인하세요.")
except Exception as e:
    print(f"SMTP 연결 중 오류가 발생했습니다: {e}")

finally:
    if 'smtp' in locals() and smtp.sock:
        smtp.quit()
        print("SMTP 연결을 종료했습니다.")
