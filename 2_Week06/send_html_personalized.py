import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage 
from email.mime.base import MIMEBase # 1. MIMEBase 임포트 (첨부파일용)
from email import encoders         # 2. encoders 임포트 (첨부파일용)
import os

# --- 1. 발송자 정보 설정 ---
sender_email = "innovation1426@gmail.com"
password = "" 

# --- 1-1. 보낼 이미지 파일 정보 ---
image_filename = "화성이미지.PNG" # 스크립트와 같은 폴더에 있어야 할 이미지 파일
image_cid = "mars_selfie_cid" # HTML에서 이미지를 부를 때 사용할 고유 ID

# --- 2. 스크립트 및 파일 경로 설정 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "mail_target_list.csv")
image_path = os.path.join(script_dir, image_filename)

# --- 3. 이미지 파일 미리 읽어두기 ---
try:
    with open(image_path, 'rb') as f:
        img_data = f.read()
    print(f"이미지 파일({image_filename})을 성공적으로 읽었습니다.")
except FileNotFoundError:
    print(f"경고: 이미지 파일({image_path})을 찾을 수 없습니다.")
    img_data = None 
except Exception as e:
    print(f"이미지 파일 읽기 중 오류 발생: {e}")
    img_data = None

# --- 4. Gmail SMTP 서버 접속 ---
try:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, password)
    print("Gmail SMTP 서버에 성공적으로 로그인했습니다.")

    # --- 5. CSV 파일 읽기 ---
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 헤더 건너뛰기
            
            # --- 6. 명단 순회하며 메일 발송 ---
            for name, receiver_email in reader:
                if not name or not receiver_email:
                    continue
                
                try:
                    # --- 6-1. (HTML+이미지) 이메일 메시지 생성 ---
                    msg = MIMEMultipart('related') 
                    
                    msg['Subject'] = Header("[사진/첨부파일] 화성 생존자 구조 요청", "utf-8")
                    msg['From'] = sender_email
                    msg['To'] = receiver_email

                    html_body = f"""
                    <html>
                    <body>
                        <h1>{name}님께,</h1>
                        <p>저는 화성에 고립된 <strong>한송희 박사</strong>입니다.</p>
                        <p>저의 생존을 증명하는 사진을 본문에 삽입하고, 원본 파일을 첨부합니다.</p>
                        <br>
                        <img src="cid:{image_cid}">
                        <br>
                        <p style="color:red; font-weight:bold;">저는 생존해 있으며, 즉각적인 구조가 필요합니다.</p>
                        <p>- 한송희 드림 -</p>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                    
                    # --- 6-2. 이미지 데이터가 있을 경우에만 첨부 ---
                    if img_data:
                        
                        # 3-A. 본문 삽입용 (Inline) 이미지 설정
                        img_inline = MIMEImage(img_data)
                        img_inline.add_header('Content-ID', f'<{image_cid}>')
                        img_inline.add_header('Content-Disposition', 'inline', filename=image_filename)
                        msg.attach(img_inline)
                        
                        # 3-B. 첨부 파일용 (Attachment) 이미지 설정
                        # (1번 문제에서 썼던 방식과 동일)
                        part_attach = MIMEBase('application', 'octet-stream')
                        part_attach.set_payload(img_data)
                        encoders.encode_base64(part_attach)
                        part_attach.add_header('Content-Disposition', 'attachment', filename=image_filename)
                        msg.attach(part_attach)
                    
                    # --- 6-3. 개별 메일 발송 ---
                    smtp.sendmail(sender_email, receiver_email, msg.as_string())
                    print(f"  -> {name}님 ({receiver_email})에게 [본문삽입+파일첨부] 메일을 성공적으로 보냈습니다.")
                    
                except Exception as e:
                    print(f"  -> {name}님 ({receiver_email})에게 메일 발송 중 오류: {e}")

    except FileNotFoundError:
        print(f"CSV 파일({csv_path})을 찾을 수 없습니다.")
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
