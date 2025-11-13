from pydantic import BaseModel, Field

class TodoItem(BaseModel):
    """
    할 일(Todo) 항목의 입출력 모델입니다.
    add_todo() (추가)와 update_todo() (수정)에서
    Request Body로 사용됩니다.
    """
    # 'task'는 최소 1글자 이상이어야 한다는 유효성 검사
    task: str = Field(min_length=1)