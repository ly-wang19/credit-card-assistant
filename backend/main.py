from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api import auth, chat, profile, credit_cards
from utils.logger import setup_logger
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# 设置日志记录器
logger = setup_logger('main')

# 创建 OAuth2 依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_optional_token(token: Optional[str] = Depends(oauth2_scheme)):
    return token

# 创建FastAPI应用
app = FastAPI(
    title="信用卡助手API",
    description="提供信用卡查询、推荐和聊天服务的API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:5174",  # Vite 备用端口
        "http://localhost:3000",  # 其他可能的开发端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api", tags=["聊天"], dependencies=[Depends(oauth2_scheme)])
app.include_router(profile.router, prefix="/api", tags=["个人中心"], dependencies=[Depends(oauth2_scheme)])
app.include_router(credit_cards.router, prefix="/api", tags=["信用卡"], dependencies=[Depends(oauth2_scheme)])

@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    logger.info("信用卡助手API服务启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info("信用卡助手API服务关闭")

@app.get("/")
async def root():
    return {"message": "信用卡助手API服务"} 