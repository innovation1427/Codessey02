import csv
import os

# 이 스크립트 파일(create_maillist.py)이 있는 폴더의 절대 경로를 가져옵니다.
script_dir = os.path.dirname(os.path.abspath(__file__))

# 저장할 CSV 파일의 이름을 정합니다.
csv_filename = "mail_target_list.csv"

# 스크립트 폴더 경로와 파일명을 합쳐서, CSV 파일이 저장될 정확한 전체 경로를 만듭니다.
file_path = os.path.join(script_dir, csv_filename)


# CSV 파일에 쓸 데이터
data = [
    ["이름", "이메일"],
    ["NASA 구조 총괄", "nasa_rescue_lead@example.com"],
    ["KARI 화성탐사팀", "kari_mars_team@example.com"],
    ["UN 우주사무국", "unoosa_urgent@example.com"]
]

try:
    # 'filename' 대신 'file_path' 변수를 사용합니다.
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"'{file_path}' 경로에 파일이 성공적으로 생성되었습니다.")
    print("   (내용을 원하는 이메일 주소로 수정해서 사용하세요.)")

except Exception as e:
    print(f"파일 생성 중 오류 발생: {e}")
