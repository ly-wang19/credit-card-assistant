from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import logging
from api.auth import get_current_user
from utils.logger import setup_logger
from config import DB_CONFIG
import mysql.connector
import bcrypt

# 设置日志记录器
logger = setup_logger('profile')

router = APIRouter()

class UserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class BankCard(BaseModel):
    bank_name: str
    card_number: str
    card_type: str
    expiry_date: date

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取用户个人信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, avatar_url, full_name, phone FROM users WHERE id = %s",
            (current_user["id"],)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
            
        return user
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_profile(
    profile: UserProfile,
    current_user: dict = Depends(get_current_user)
):
    """更新用户个人信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 如果要更改密码，先验证当前密码
        if profile.new_password:
            if not profile.current_password:
                raise HTTPException(status_code=400, detail="需要提供当前密码")
                
            cursor.execute(
                "SELECT password_hash FROM users WHERE id = %s",
                (current_user["id"],)
            )
            current_hash = cursor.fetchone()[0]
            
            if not bcrypt.checkpw(profile.current_password.encode(), current_hash.encode()):
                raise HTTPException(status_code=400, detail="当前密码不正确")
                
            new_hash = bcrypt.hashpw(profile.new_password.encode(), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_hash, current_user["id"])
            )
        
        # 更新其他信息
        update_fields = []
        update_values = []
        
        if profile.username:
            update_fields.append("username = %s")
            update_values.append(profile.username)
        if profile.email:
            update_fields.append("email = %s")
            update_values.append(profile.email)
        if profile.full_name:
            update_fields.append("full_name = %s")
            update_values.append(profile.full_name)
        if profile.phone:
            update_fields.append("phone = %s")
            update_values.append(profile.phone)
            
        if update_fields:
            sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            update_values.append(current_user["id"])
            cursor.execute(sql, update_values)
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "个人信息更新成功"}
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """上传头像"""
    try:
        # TODO: 实现文件上传逻辑
        # 1. 验证文件类型
        # 2. 保存文件
        # 3. 更新数据库中的avatar_url
        return {"message": "头像上传成功"}
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cards")
async def get_user_cards(current_user: dict = Depends(get_current_user)):
    """获取用户的银行卡列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_cards WHERE user_id = %s",
            (current_user["id"],)
        )
        cards = cursor.fetchall()
        cursor.close()
        conn.close()
        return cards
    except Exception as e:
        logger.error(f"获取银行卡列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cards")
async def add_bank_card(
    card: BankCard,
    current_user: dict = Depends(get_current_user)
):
    """添加银行卡"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_cards 
            (user_id, bank_name, card_number, card_type, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (current_user["id"], card.bank_name, card.card_number, 
             card.card_type, card.expiry_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "银行卡添加成功"}
    except Exception as e:
        logger.error(f"添加银行卡失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cards/{card_id}")
async def delete_bank_card(
    card_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除银行卡"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_cards WHERE id = %s AND user_id = %s",
            (card_id, current_user["id"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "银行卡删除成功"}
    except Exception as e:
        logger.error(f"删除银行卡失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 