import datetime
from pydantic import BaseModel, field_validator

# 1. (기존) 질문 조회용 스키마
class Question(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime.datetime

    class Config:
        from_attributes = True

# --- [새로 추가된 부분] ---
# 2. 질문 등록용 스키마 (QuestionCreate)
# 사용자에게 입력받을 데이터만 정의합니다.
class QuestionCreate(BaseModel):
    subject: str
    content: str

    # 3. 빈 값 체크 (validator)
    # 제목과 내용이 공백(빈 문자열)인지 확인합니다.
    @field_validator('subject', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v