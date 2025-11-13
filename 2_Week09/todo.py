import csv
import os
from fastapi import FastAPI, APIRouter, HTTPException, Path, status
# ⭐️ 1. (신규) CORS 미들웨어 임포트
from fastapi.middleware.cors import CORSMiddleware
from model import TodoItem 
from typing import List, Dict, Any

# --- 1. 설정 및 전역 변수 ---
CSV_FILE = "todo.csv" 
todo_list: List[Dict[str, str]] = [] 

# --- (CSV 헬퍼 함수들은 이전과 동일...) ---

def save_all_todos_to_csv():
    global todo_list
    try:
        with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["task"])
            writer.writeheader()
            writer.writerows(todo_list)
    except Exception as e:
        print(f"❌ CSV 전체 저장 중 오류 발생: {e}")

def load_todos_from_csv():
    global todo_list
    todo_list = [] 
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                todo_list.append(row)
        print(f"✅ CSV({CSV_FILE})에서 {len(todo_list)}개 작업을 로드했습니다.")
    except FileNotFoundError:
        save_all_todos_to_csv()
        print(f"✅ {CSV_FILE} 파일을 새로 생성했습니다.")
    except Exception as e:
        print(f"❌ CSV 로드 중 오류 발생: {e}")

def append_todo_to_csv(todo: Dict[str, str]):
    try:
        with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["task"])
            writer.writerow(todo)
    except Exception as e:
        print(f"❌ CSV 추가 저장 중 오류 발생: {e}")

# --- 3. FastAPI 앱 및 라우터 설정 ---
app = FastAPI(title="Han's Mars-Earth TO-DO API (v2)")

# --- ⭐️ 2. (신규) CORS 미들웨어 추가 ---
# 이 서버가 모든 '출신'의 요청을 허용하도록 설정합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 방식 (GET, POST, PUT, DELETE 등) 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
# ---------------------------------

router = APIRouter()

# --- (헬퍼: ID 유효성 검사 - 이전과 동일) ---
def get_todo_or_404(todo_id: int):
    if 0 <= todo_id < len(todo_list):
        return todo_list[todo_id]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Todo with ID {todo_id} not found")

# --- (4. API 라우트 정의 - 이전과 동일) ---

@router.post("/todos", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def add_todo(todo: TodoItem):
    global todo_list
    new_todo_dict = todo.model_dump()
    todo_list.append(new_todo_dict)
    append_todo_to_csv(new_todo_dict)
    new_id = len(todo_list) - 1
    return {"message": "Todo added successfully", "new_todo": {"id": new_id, **new_todo_dict}}

@router.get("/todos", response_model=Dict[str, List[Dict[str, Any]]])
async def retrieve_todo():
    todos_with_ids = []
    for i, todo in enumerate(todo_list):
        todos_with_ids.append({"id": i, **todo})
    return {"todos": todos_with_ids}

@router.get("/todos/{todo_id}", response_model=Dict[str, Any])
async def get_single_todo(todo_id: int = Path(..., title="The ID of the todo to get", ge=0)):
    todo = get_todo_or_404(todo_id)
    return {"id": todo_id, **todo}

@router.put("/todos/{todo_id}", response_model=Dict[str, Any])
async def update_todo(todo_item: TodoItem, 
                    todo_id: int = Path(..., title="The ID of the todo to update", ge=0)):
    global todo_list
    get_todo_or_404(todo_id)
    updated_todo_dict = todo_item.model_dump()
    todo_list[todo_id] = updated_todo_dict
    save_all_todos_to_csv()
    return {"message": "Todo updated successfully", "updated_todo": {"id": todo_id, **updated_todo_dict}}

@router.delete("/todos/{todo_id}", response_model=Dict[str, Any])
async def delete_single_todo(todo_id: int = Path(..., title="The ID of the todo to delete", ge=0)):
    global todo_list
    todo = get_todo_or_404(todo_id)
    deleted_todo = todo_list.pop(todo_id)
    save_all_todos_to_csv()
    return {"message": "Todo deleted successfully", "deleted_todo": {"id": todo_id, **deleted_todo}}

# --- 5. 앱 시작 이벤트 및 라우터 연결 ---
@app.on_event("startup")
async def startup_event():
    load_todos_from_csv()

app.include_router(router, prefix="/api")