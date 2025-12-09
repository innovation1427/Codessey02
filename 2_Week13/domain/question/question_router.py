from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import datetime # 날짜 생성을 위해 추가

# 상위 폴더의 모듈을 가져옵니다.
from database import get_db
from models import Question
# 스키마 파일(question_schema)을 가져옵니다.
from domain.question import question_schema

router = APIRouter(
    prefix="/api/question",
)

# 1. 질문 목록 조회 (기존)
@router.get("/list", response_model=List[question_schema.Question])
def question_list(db: Session = Depends(get_db)):
    """
    데이터베이스에서 질문 목록 전체를 조회하여 반환합니다.
    """
    _question_list = db.query(Question).all()
    return _question_list

# --- [새로 추가된 부분] ---
# 2. 질문 등록 (POST /api/question/create)
@router.post("/create", status_code=204)
def question_create(_question_create: question_schema.QuestionCreate, 
                    db: Session = Depends(get_db)):
    """
    질문을 등록합니다.
    - subject: 제목
    - content: 내용
    """
    # 3. ORM 모델 객체 생성
    # 스키마(QuestionCreate)로 받은 데이터를 ORM 모델(Question)로 변환합니다.
    new_question = Question(
        subject=_question_create.subject,
        content=_question_create.content,
        create_date=datetime.datetime.now() # 현재 시간 자동 입력
    )
    
    # 4. 데이터베이스에 저장
    db.add(new_question) # 세션에 추가
    db.commit()          # 실제 DB에 저장 (커밋)