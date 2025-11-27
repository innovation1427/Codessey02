from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. SQLite 데이터베이스 파일 경로 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"

# 2. 데이터베이스 엔진 생성
# connect_args={"check_same_thread": False}는 SQLite에서만 필요한 설정입니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 데이터베이스 세션 생성
# autocommit=False: 커밋을 수동으로 하겠다는 설정 (트랜잭션 관리)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. ORM 모델들이 상속받을 기본 클래스(Base) 생성
Base = declarative_base()

# --- [새로 추가된 부분] ---
# 5. Dependency Injection(의존성 주입)을 위한 함수
# API 요청이 올 때마다 DB 세션을 열고, 작업이 끝나면 닫아주는 역할을 합니다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()