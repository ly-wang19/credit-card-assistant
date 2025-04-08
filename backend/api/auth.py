import os
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError
import bcrypt
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from config import settings
from database.db import get_db_connection

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# 测试账号
TEST_USER = {
    "username": "test",
    "email": "test@example.com",
    "password": bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode(),
    "id": 1
}

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 增加到24小时

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise credentials_exception
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (token_data.username,))
        user = cursor.fetchone()
        if user is None:
            raise credentials_exception
        return user
    finally:
        cursor.close()
        db.close()

@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    if user.username == TEST_USER["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    try:
        # 连接数据库
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
            
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 对密码进行哈希处理
        password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        
        # 插入新用户
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (user.username, user.email, password_hash)
        )
        db.commit()
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.debug(f"尝试登录用户: {form_data.username}")
    db = None
    cursor = None
    
    try:
        # 连接数据库
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            logger.debug("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database connection error: {str(e)}"
            )

        # 查询用户
        try:
            if "@" in form_data.username:
                logger.debug(f"使用邮箱登录: {form_data.username}")
                cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
            else:
                logger.debug(f"使用用户名登录: {form_data.username}")
                cursor.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
            
            user = cursor.fetchone()
            logger.debug(f"查询到的用户信息: {user}")
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User query error: {str(e)}"
            )

        if not user:
            logger.warning(f"用户不存在: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 验证密码
        try:
            logger.debug("开始验证密码")
            password_bytes = form_data.password.encode()
            stored_hash = user["password_hash"]
            stored_hash_bytes = stored_hash.encode()
            
            logger.debug(f"输入的密码: {form_data.password}")
            logger.debug(f"存储的密码哈希: {stored_hash}")
            
            password_matches = bcrypt.checkpw(password_bytes, stored_hash_bytes)
            logger.debug(f"密码验证结果: {password_matches}")
            
            if not password_matches:
                logger.warning(f"密码错误: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username/email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password verification error: {str(e)}"
            )

        # 生成访问令牌
        try:
            logger.debug("开始生成访问令牌")
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user["username"]}, expires_delta=access_token_expires
            )
            logger.debug(f"生成访问令牌成功: {user['username']}")
            
            response_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                }
            }
            logger.debug(f"登录成功，返回数据: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"生成访问令牌失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token generation error: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录过程出现未知错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error during login: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
        logger.debug("数据库连接已关闭")

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, username, email, full_name FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        db.close() 