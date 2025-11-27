from fastapi import FastAPI

# FastAPI 앱 생성
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "한송희 박사의 화성 게시판 서버가 정상 작동 중입니다!"}