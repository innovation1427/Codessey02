import csv
import os
from fastapi import FastAPI, APIRouter, HTTPException
# Pydantic의 BaseModel을 사용해 Dict 타입을 정의하고 유효성을 검사합니다.
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- 1. 설정 및 전역 변수 ---

# 제약사항 #3: CSV 파일 사용
CSV_FILE = "todo.csv" 
# 수행과제 #5: 'todo_list' 리스트 객체
todo_list: List[Dict[str, str]] = [] 

# --- 2. Pydantic 모델 정의 (Dict 타입 입출력용) ---

# 'add_todo'의 입력(Input) 모델
# 수행과제 #8: 빈 값 입력을 막기 위해 최소 길이 1 설정 (constr)
class TodoIn(BaseModel):
    task: str = Field(min_length=1)

# --- 3. CSV 헬퍼 함수 ---

def load_todos_from_csv():
    """서버 시작 시 CSV에서 todo_list로 데이터를 로드합니다."""
    global todo_list
    todo_list = [] # 매번 새로 로드하기 위해 초기화
    try:
        # CSV 파일을 딕셔너리 형태로 읽어옵니다.
        with open(CSV_FILE, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                todo_list.append(row)
        print(f"✅ CSV({CSV_FILE})에서 {len(todo_list)}개 작업을 로드했습니다.")
    except FileNotFoundError:
        # 파일이 없으면 헤더("task")만 있는 새 파일 생성
        try:
            with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["task"])
                writer.writeheader()
            print(f"✅ {CSV_FILE} 파일을 새로 생성했습니다.")
        except Exception as e:
            print(f"❌ CSV 파일 생성 중 오류 발생: {e}")
    except Exception as e:
        print(f"❌ CSV 로드 중 오류 발생: {e}")

def save_todo_to_csv(todo: Dict[str, str]):
    """새 작업을 CSV 파일에 '추가'합니다. (Constraint #3)"""
    try:
        # 'a' (append) 모드로 파일을 열어 새 작업을 추가합니다.
        with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["task"])
            writer.writerow(todo)
    except Exception as e:
        print(f"❌ CSV 저장 중 오류 발생: {e}")

# --- 4. FastAPI 앱 및 라우터 설정 ---

app = FastAPI(title="Han's Mars-Earth TO-DO API")
# 수행과제 #6: APIRouter 클래스 사용
router = APIRouter()

# --- 5. API 라우트 정의 ---

# 수행과제 #6 (add_todo)
@router.post("/todos", response_model=Dict[str, Any])
async def add_todo(todo: TodoIn):
    """
    (1) 새로운 할 일을 todo_list와 CSV 파일에 추가합니다.
    (2) POST 방식입니다.
    (3) 입출력은 Dict 타입입니다.
    """
    global todo_list
    # Pydantic 모델을 Python 딕셔너리로 변환
    new_todo_dict = todo.model_dump()
    
    # 수행과제 #6.1: todo_list에 추가
    todo_list.append(new_todo_dict)
    
    # 제약사항 #3: CSV에 저장
    save_todo_to_csv(new_todo_dict)
    
    # 수행과제 #6.1: Dict 타입으로 반환
    return {"message": "Todo added successfully", "new_todo": new_todo_dict}

# 수행과제 #6 (retrieve_todo)
@router.get("/todos", response_model=Dict[str, List[Dict[str, str]]])
async def retrieve_todo():
    """
    (1) 현재 todo_list의 모든 항목을 가져옵니다.
    (2) GET 방식입니다.
    (3) 입출력은 Dict 타입입니다.
    """
    # 수행과제 #6.2: todo_list를 가져옴
    # 수행과제 #6.2: Dict 타입으로 반환
    return {"todos": todo_list}

# --- 6. 앱 시작 이벤트 (Startup Event) ---

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 CSV 파일에서 데이터를 로드합니다."""
    load_todos_from_csv()

# --- 7. 라우터 앱에 연결 ---
app.include_router(router, prefix="/api")

# (이 파일은 'uvicorn todo:app --reload' 명령어로 실행합니다)