from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # 웹 서버의 뼈대
import datetime             # 현재 시간 찍을 때 사용
import json                 # /metrics, /whoami에서 JSON(컴퓨터 친화적 형식)으로 응답
import urllib.request       # 외부(인터넷)로 간단히 요청 보낼 때 사용(표준 라이브러리)
import urllib.error         # 외부 요청이 실패할 때의 예외(오류) 처리
import os                   # 파일이 있는지 확인할 때 사용

# 서버가 열릴 주소와 포트 번호를 정합니다.
HOST = "0.0.0.0"            # 0.0.0.0 = "모든 곳에서 들어오는 연결을 받겠다"는 뜻
PORT = 8080                 # 과제에서 지정한 포트 번호

# 글자가 깨지지 않도록 UTF-8로 고정합니다.
ENCODING = "utf-8"

# 이 서버가 받은 요청의 개수를 세기 위한 작은 저장소(사전형)
# - total: 전체 요청 수
# - by_path: 주소(예: "/", "/metrics")별로 몇 번 왔는지 세기
REQUEST_COUNTER = {
    "total": 0,
    "by_path": {}
}

# 간단한 도우미 함수: 콘솔(터미널)에 보기 좋게 로그(기록) 출력
def log_console(message: str):
    # 현재 시간을 예쁘게 만들어서 앞에 붙입니다.
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")

# 접속자의 IP로 대략적인 위치를 알아보는 함수(선택 기능)
# - 무료 공개 API(ip-api.com)를 사용합니다.
# - 외부 요청이므로, 회사/학교 네트워크 설정에 따라 막힐 수도 있습니다.
# - 127.0.0.1(내 컴퓨터)로 접속하면 위치는 "localhost"로 표기합니다.
def lookup_location_by_ip(ip: str):
    # 만약 접속이 내 컴퓨터(127.0.0.1 또는 ::1)이면 굳이 인터넷으로 물어보지 않습니다.
    if ip in ("127.0.0.1", "::1"):
        return {"ip": ip, "location": "localhost", "org": None}

    # 외부 API 주소를 만듭니다. (표준 라이브러리 urllib으로 호출)
    url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,org,query"

    try:
        # 인터넷으로 요청을 보냅니다.
        with urllib.request.urlopen(url, timeout=4) as resp:
            # 받은 내용을 UTF-8로 읽어서 파이썬 사전으로 바꿉니다.
            data = json.loads(resp.read().decode(ENCODING))
            # status가 success이면 우리가 보고 싶은 정보가 들어 있습니다.
            if data.get("status") == "success":
                country = data.get("country", "")
                region = data.get("regionName", "")
                city = data.get("city", "")
                org = data.get("org", None)
                # 사람이 읽기 편한 한 줄 문장으로 만듭니다.
                loc_text = " ".join([p for p in [country, region, city] if p])
                return {"ip": ip, "location": loc_text or None, "org": org}
    except Exception:
        # 인터넷이 안 되거나, API가 답을 안 줄 수도 있으니 조용히 무시합니다.
        pass

    # 실패했을 때는 None 값들을 돌려줍니다.
    return {"ip": ip, "location": None, "org": None}

# 실제로 요청을 받아서 처리하는 "직원" 클래스(사람 1명이라고 생각하면 편합니다)
class SpacePirateHandler(BaseHTTPRequestHandler):
    # 서버 버전 문자열(그냥 보이는 이름 정도)
    server_version = "SpacePirateHTTP/0.1"

    # 기본 로그(영문, 지저분)를 끄고, 우리가 예쁘게 찍는 log_console만 쓰겠습니다.
    def log_message(self, format, *args):
        return

    # 웹 브라우저가 "GET" 방식으로 요청했을 때 여기로 들어옵니다.
    def do_GET(self):
        # 1) 접속한 사람의 IP 주소를 가져옵니다.
        client_ip = self.client_address[0]

        # 2) 이번 요청을 기록(카운트)합니다.
        REQUEST_COUNTER["total"] += 1
        REQUEST_COUNTER["by_path"][self.path] = REQUEST_COUNTER["by_path"].get(self.path, 0) + 1

        # 3) 터미널에 접속 로그를 남깁니다. (요구사항: 접속 시간, 클라이언트 IP)
        log_console(f"접속: IP={client_ip}  Path={self.path}")

        # 4) 위치 정보도 한 번 시도해서 콘솔에 같이 보여줍니다. (요구사항: IP 기반 위치 확인)
        who = lookup_location_by_ip(client_ip)
        if who.get("location"):
            log_console(f"위치 추정: {who['location']}  (기관/통신사: {who.get('org')})")

        # 5) 주소에 따라 다르게 응답합니다.
        if self.path in ("/", "/index.html"):
            # index.html 파일이 같은 폴더에 있는지 확인합니다.
            if os.path.exists("index.html"):
                # 파일을 읽어서 브라우저로 보냅니다.
                with open("index.html", "rb") as f:
                    content = f.read()
                # 200 OK(정상) 상태를 먼저 보냅니다. (요구사항: 200번 메시지)
                self.send_response(200)
                # 브라우저가 "이건 HTML이고 UTF-8이다"를 알 수 있게 머리글을 붙입니다.
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()  # 여기까지가 "머리글". 이제 "몸통(내용)"을 보냅니다.
                self.wfile.write(content)
            else:
                # index.html이 없다면 간단한 안내 페이지를 즉석에서 만들어 보냅니다.
                fallback = "<h1>index.html 파일을 이 폴더에 두세요.</h1>".encode(ENCODING)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(fallback)))
                self.end_headers()
                self.wfile.write(fallback)

        elif self.path == "/metrics":
            # 지금까지 몇 번 요청이 들어왔는지 JSON으로 보여줍니다.
            body = json.dumps(REQUEST_COUNTER, ensure_ascii=False, indent=2).encode(ENCODING)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/whoami":
            # 접속자의 IP와 대략적인 위치를 JSON으로 보여줍니다.
            body = json.dumps(who, ensure_ascii=False, indent=2).encode(ENCODING)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        else:
            # 모르는 주소면 404 Not Found(찾을 수 없음)로 답합니다.
            self.send_error(404, "Not Found")

# 프로그램이 바로 실행될 때만 아래 코드가 돌아가도록 합니다.
if __name__ == "__main__":
    # ThreadingHTTPServer를 써서 요청이 몰려도 동시에 처리할 수 있게 합니다.
    # (한 명씩만 처리하는 서버보다 덜 답답합니다.)
    httpd = ThreadingHTTPServer((HOST, PORT), SpacePirateHandler)
    log_console(f"서버 시작: http://127.0.0.1:{PORT} (또는 이 컴퓨터의 IP:{PORT})")

    try:
        # 서버를 계속 돌립니다. (Ctrl + C 로 멈출 수 있습니다.)
        httpd.serve_forever()
    except KeyboardInterrupt:
        # 사용자가 멈추면 여기로 와서 깔끔히 종료합니다.
        log_console("서버를 종료합니다.")
    finally:
        httpd.server_close()
