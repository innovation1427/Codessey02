import socket      # 네트워크 통신(전화기 같은 역할)을 할 수 있게 해주는 기본 도구
import threading   # 동시에 여러 사람과 대화(멀티태스킹)를 할 수 있게 해주는 도구

# 서버가 열릴 주소와 포트 번호를 정해요
HOST = "0.0.0.0"   # 0.0.0.0 은 '내 컴퓨터로 들어오는 모든 연결을 받겠다'는 뜻
PORT = 5000        # 전화기로 치면 '내선 번호' 같은 것. 아무 숫자나 정하면 됨 (보통 1024~65535)

# 현재 채팅방에 들어와 있는 사람들의 정보를 저장할 곳
clients = {}        # 소켓(전화선) -> 이름(닉네임)
name_to_sock = {}   # 이름(닉네임) -> 소켓(전화선)

# 여러 사람이 동시에 들어와도 순서가 꼬이지 않게 '문 잠금장치' 같은 걸 씀
lock = threading.Lock()

ENC = "utf-8"       # 글자 깨지지 않게 'UTF-8' 방식으로 메시지를 주고받음


# 특정 사람에게 메시지를 보내는 함수
def send_line(sock, msg: str):
    try:
        sock.sendall((msg + "\n").encode(ENC))  # 글자를 UTF-8로 바꿔서 보내기
    except:
        pass  # 실패하면 그냥 무시 (나중에 정리될 거니까)


# 채팅방 안에 있는 모든 사람에게 메시지를 보내는 함수
def broadcast(msg: str, exclude_sock=None):
    with lock:  # 다른 사람이 동시에 바꿀 수 있으니까 잠금장치 걸기
        targets = [s for s in clients.keys() if s is not exclude_sock]  # 보낼 사람 목록
    for s in targets:
        send_line(s, msg)  # 한 명씩 메시지 보내기


# 새로 들어온 사람에게 이름(닉네임)을 받아서 등록하는 함수
def ensure_unique_name(sock):
    send_line(sock, "닉네임을 입력하세요:")  # 안내 메시지 보내기
    f = sock.makefile("r", encoding=ENC, newline="\n")  # 읽기 편하게 파일처럼 바꿔줌
    while True:
        line = f.readline()  # 한 줄 읽기 (사람이 입력한 것)
        if not line:  # 아무 것도 없으면 (즉, 연결이 끊겼으면)
            return None
        name = line.strip()  # 이름 앞뒤 공백 제거
        if not name:  # 이름이 비어있으면 다시 입력 요청
            send_line(sock, "빈 닉네임은 안돼요. 다시 입력:")
            continue
        with lock:
            if name in name_to_sock:  # 이미 같은 이름이 있으면
                send_line(sock, f"'{name}'는 이미 사용 중입니다. 다른 닉네임을 입력하세요:")
            else:
                # 사용 가능한 이름이면 등록하기
                name_to_sock[name] = sock
                clients[sock] = name
                return name  # 이 이름을 최종으로 사용


# 사람이 나갔을 때 처리하는 함수
def remove_client(sock, announce=True):
    with lock:
        name = clients.get(sock)  # 소켓으로 이름 찾기
        if name:
            del clients[sock]  # 사람 목록에서 제거
            if name in name_to_sock:
                del name_to_sock[name]  # 이름-소켓 연결도 제거
    if announce and name:  # 퇴장 알림을 켜둔 경우
        broadcast(f"{name}님이 퇴장하셨습니다.")  # 모두에게 알림
    try:
        sock.close()  # 전화기 끊기
    except:
        pass


# 귓속말 기능 처리하는 함수
def handle_whisper(sender_name, text, sock):
    parts = text.split(maxsplit=2)  # "/w 대상이름 메시지" 형태로 나누기
    if len(parts) < 3:  # 형식이 잘못되면
        send_line(sock, "사용법: /w <닉네임> <메시지>")
        return
    _, target_name, msg = parts
    with lock:
        target_sock = name_to_sock.get(target_name)  # 대상 이름으로 전화선 찾기
    if not target_sock:  # 대상이 없으면 안내
        send_line(sock, f"'{target_name}' 닉네임을 찾을 수 없습니다.")
        return
    # 상대방에게 메시지 보내기
    send_line(target_sock, f"(귓){sender_name}> {msg}")
    # 본인에게도 보냈다는 표시
    if target_sock is not sock:
        send_line(sock, f"(귓→{target_name}) {sender_name}> {msg}")


# 한 사람과 통신하는 메인 함수 (사람 1명당 1개 스레드 실행)
def handle_client(sock, addr):
    name = ensure_unique_name(sock)  # 이름 받기
    if not name:  # 이름을 못 받으면 그냥 종료
        remove_client(sock, announce=False)
        return

    broadcast(f"📥 {name}님이 입장하셨습니다.")  # 모두에게 입장 알림
    send_line(sock, "명령어: /종료  |  귓속말: /w 닉 메시지")
    send_line(sock, "채팅을 시작해 보세요!")

    f = sock.makefile("r", encoding=ENC, newline="\n")  # 입력을 줄 단위로 받음
    for line in f:  # 계속 줄 단위로 읽음
        msg = line.strip()
        if not msg:  # 빈 줄이면 무시
            continue
        if msg == "/종료":  # 종료 명령어면
            send_line(sock, "연결을 종료합니다. 안녕히 가세요!")
            break
        if msg.startswith("/w ") or msg.startswith("/to ") or msg.startswith("/귓속말 "):
            handle_whisper(name, msg, sock)  # 귓속말 처리
            continue
        broadcast(f"{name}> {msg}")  # 일반 메시지면 모두에게 보내기

    remove_client(sock, announce=True)  # 연결 끝나면 정리


# 서버 시작 함수
def accept_loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 서버 재시작 시 충돌 방지
        s.bind((HOST, PORT))  # 주소와 포트에 전화기 연결
        s.listen()  # "이제 손님 받아요!" 대기 상태
        print(f"서버 시작: {HOST}:{PORT}")
        while True:
            sock, addr = s.accept()  # 새 손님이 오면 연결 수락
            t = threading.Thread(target=handle_client, args=(sock, addr), daemon=True)
            t.start()  # 사람마다 따로 스레드를 만들어 처리

if __name__ == "__main__":
    accept_loop()  # 서버 실행 시작
