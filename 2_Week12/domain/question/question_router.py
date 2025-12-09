from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
# List 타입 힌팅을 위해 추가
from typing import List 

from database import get_db
from models import Question
# ⭐️ 만든 스키마(Question)를 가져옵니다.
from domain.question import question_schema

router = APIRouter(
    prefix="/api/question",
)

# ⭐️ response_model을 추가하여 반환 데이터의 형식을 Pydantic 스키마로 고정합니다.
# List[question_schema.Question]은 "Question 스키마 여러 개가 리스트로 나간다"는 뜻입니다.
@router.get("/list", response_model=List[question_schema.Question])
def question_list(db: Session = Depends(get_db)):
    """
    데이터베이스에서 질문 목록 전체를 조회하여 반환합니다.
    """
    _question_list = db.query(Question).all()
    return _question_list