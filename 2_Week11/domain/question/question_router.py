from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 상위 폴더(루트)에 있는 모듈들을 가져오기 위해 임포트합니다.
# database.py의 get_db 함수와 models.py의 Question 모델이 필요합니다.
from database import get_db
from models import Question

# 1. APIRouter 생성 (prefix 설정)
router = APIRouter(
    prefix="/api/question",
)

# 2. 질문 목록 조회 함수 (GET /api/question/list)
@router.get("/list")
def question_list(db: Session = Depends(get_db)):
    """
    데이터베이스에서 질문 목록 전체를 조회하여 반환합니다.
    SQLAlchemy ORM을 사용합니다.
    """
    # db.query(Question).all()은 'SELECT * FROM question'과 같은 역할을 합니다.
    _question_list = db.query(Question).all()
    return _question_list