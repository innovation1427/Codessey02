from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys

# ---------------------------------------------------------
# [중요] 1. 현재 폴더 경로를 추가해서 models.py와 database.py를 찾을 수 있게 함
sys.path.append(os.getcwd())

# [중요] 2. 우리가 작성한 모델과 데이터베이스 설정 가져오기
from database import Base
# Question 모델을 임포트해야 Alembic이 "아, 이런 테이블을 만들어야 하는구나" 하고 인식합니다.
from models import Question

# 3. Alembic 설정 객체 가져오기
config = context.config

# 4. 로깅 설정 (alembic.ini의 설정을 따름)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# [중요] 5. 메타데이터 연결
# 이 부분이 없으면 "MetaData object not found" 에러가 발생합니다.
target_metadata = Base.metadata
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()