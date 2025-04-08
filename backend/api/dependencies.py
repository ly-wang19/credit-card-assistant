"""
数据库依赖
实现数据库会话管理和依赖注入
"""

from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from ..config import settings

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL)

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close() 