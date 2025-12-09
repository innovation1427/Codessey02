import datetime
from pydantic import BaseModel

# 질문(Question) 스키마 정의
class Question(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime.datetime

    # 내부 클래스 Config 설정
    class Config:
        # Pydantic v2에서는 from_attributes = True 로 사용합니다.
        # (구버전의 orm_mode = True 와 같은 역할입니다)
        # ORM 객체(SQLAlchemy)를 Pydantic 모델로 읽을 수 있게 해줍니다.
        from_attributes = True 
        # orm_mode = True # Pydantic v1을 쓴다면 이 주석을 해제하세요.