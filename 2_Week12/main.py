from fastapi import FastAPI
# domain/question 폴더 안에 있는 question_router 파일을 가져옵니다.
from domain.question import question_router

app = FastAPI()

# 1. 라우터 등록 (include_router)
# 이제 '/api/question'으로 시작하는 모든 요청은 question_router가 처리합니다.
app.include_router(question_router.router)

@app.get("/")
def read_root():
    return {"message": "한송희 박사의 화성 게시판 서버가 정상 작동 중입니다!"}