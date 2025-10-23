import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import os # 파일 경로를 다루기 위해 os 모듈 추가

# 1. 보내는 사람, 받는 사람, 앱 비밀번호 설정
sender_email = "innovation1426@gmail.com"
receiver_email = "alsgur1426@naver.com"
password = ""

# 2. 이메일 메시지 설정 (MIMEMultipart)
# MIMEMultipart는 여러 부분(본문, 첨부파일 등)을 담을 수 있는 컨테이너 역할
msg = MIMEMultipart()
msg['Subject'] = Header("파이썬 SMTP 테스트 메일 (첨부파일 포함)", "utf-8")
msg['From'] = sender_email
msg['To'] = receiver_email

# 2-1. 이메일 본문 추가 (MIMEText)
body = "이것은 파이썬으로 보낸 테스트 이메일입니다.\n첨부파일을 확인해주세요."
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 2-2. 첨부 파일 추가
file_path = "Exfile.txt" # 첨부할 파일 이름

# 첨부할 파일을 미리 생성
with open(file_path, 'w') as f:
    f.write("이것은 첨부된 텍스트 파일의 내용입니다.")

# 파일이 존재하는지 확인
if os.path.exists(file_path):
    try:
        with open(file_path, 'rb') as f: # 파일을 바이너리(binary) 읽기 모드로 엶
            # MIMEBase 객체 생성 ('application/octet-stream'은 모든 종류의 이진 데이터를 의미)
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        # Base64로 인코딩 (이메일로 전송할 수 있는 형식으로 변환)
        encoders.encode_base64(part)
        
        # 파일 이름을 헤더에 추가
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        
        # 메시지 컨테이너에 첨부파일 추가
        msg.attach(part)
    except Exception as e:
        print(f"파일 첨부 중 오류 발생: {e}")

# 3. SMTP 서버에 로그인 후 이메일 발송 (이전 코드와 동일)
try:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, password)
    smtp.sendmail(sender_email, receiver_email, msg.as_string())
    print("첨부파일이 포함된 메일을 성공적으로 보냈습니다.")

except smtplib.SMTPAuthenticationError:
    print("로그인 실패: 이메일 주소 또는 앱 비밀번호를 확인하세요.")
except Exception as e:
    print(f"메일 발송 중 오류가 발생했습니다: {e}")

finally:
    if 'smtp' in locals() and smtp.sock:
        smtp.quit()
    # 테스트용으로 생성한 첨부 파일 삭제
    if os.path.exists(file_path):
        os.remove(file_path)