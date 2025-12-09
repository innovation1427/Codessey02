from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class Question(Base):
    """
    질문(Question) 테이블 모델 정의
    """
    __tablename__ = "question"  # 데이터베이스에 생성될 실제 테이블 이름

    id = Column(Integer, primary_key=True, index=True)   # 고유 번호 (PK)
    subject = Column(String, nullable=False)             # 제목
    content = Column(Text, nullable=False)               # 내용
    create_date = Column(DateTime, nullable=False)       # 작성 일시