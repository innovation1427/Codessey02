import socket     # 네트워크 통신용
import threading  # 동시에 보내고 받기 위해 필요
import sys        # 키보드 입력을 다루기 위해 필요

HOST = "127.0.0.1"  # 서버 주소 (같은 컴퓨터에서 테스트하면 127.0.0.1)
PORT = 5000         # 서버와 똑같이 맞춰야 함
ENC = "utf-8"       # 글자 깨지지 않게 UTF-8 사용


# 서버에서 오는 메시지를 계속 받는 함수
def recv_loop(sock):
    try:
        f = sock.makefile("r", encoding=ENC, newline="\n")  # 서버에서 오는 걸 줄 단위로 읽기
        for line in f:  # 계속 읽음
            print(line.strip())  # 화면에 출력
    except:
        pass
    finally:
        sock.close()  # 끝나면 전화기 끊기


# 내가 입력한 걸 서버로 계속 보내는 함수
def send_loop(sock):
    try:
        for line in sys.stdin:  # 키보드에서 한 줄 입력할 때마다
            msg = line.strip()
            sock.sendall((msg + "\n").encode(ENC))  # 서버로 전송
            if msg == "/종료":  # '/종료' 입력하면 종료
                break
    except:
        pass
    finally:
        sock.close()


# 메인 실행 부분
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # 서버에 연결
        # 서버에서 오는 메시지를 받는 전용 스레드 만들기
        t_recv = threading.Thread(target=recv_loop, args=(s,), daemon=True)
        t_recv.start()
        # 메인 스레드는 내가 입력한 걸 보내는 역할
        send_loop(s)

if __name__ == "__main__":
    main()
