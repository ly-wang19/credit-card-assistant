"""
配置文件
包含数据库连接、API密钥、爬虫配置等系统配置项
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional, Dict

# 加载环境变量
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USERNAME", "root"),
    "password": os.getenv("DB_PASSWORD", "1996129.yin"),
    "database": os.getenv("DB_DATABASE", "credit_card_db")
}

class Settings(BaseSettings):
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "1996129.yin")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "credit_card_db")
    PORT: str = "3001"
    
    DATABASE_URL: str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    VECTOR_DB_URL: str = "postgresql://user:password@localhost:5432/vector_db"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "信用卡用卡助手"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 爬虫配置
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_RETRY_TIMES: int = 3
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    
    # RAG配置
    VECTOR_DIMENSION: int = 1536
    MAX_RETRIEVAL_DOCS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 