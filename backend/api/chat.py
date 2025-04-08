import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from agent.core import CreditCardAgent
from llm_service.deepseek_adapter import DeepSeekAdapter
from config import DB_CONFIG
from utils.logger import setup_logger
from api.auth import get_current_user
import mysql.connector

# 设置日志记录器
logger = setup_logger('chat')

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

def save_chat_history(user_id: int, message: str, response: str):
    """保存聊天记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, message, response) VALUES (%s, %s, %s)",
            (user_id, message, response)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"保存聊天记录失败: {str(e)}")

def get_chat_history(user_id: int, limit: int = 10) -> List[Dict]:
    """获取聊天历史记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        return history
    except Exception as e:
        logger.error(f"获取聊天记录失败: {str(e)}")
        return []

def search_credit_cards(keyword: str) -> List[Dict]:
    """从知识库搜索信用卡信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建搜索SQL
        sql = """
        SELECT * FROM credit_cards 
        WHERE bank_name LIKE %s 
        OR card_name LIKE %s 
        OR card_level LIKE %s 
        OR benefits LIKE %s
        LIMIT 5
        """
        search_term = f"%{keyword}%"
        cursor.execute(sql, (search_term, search_term, search_term, search_term))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logger.info(f"搜索到 {len(results)} 条信用卡信息")
        return results
    except Exception as e:
        logger.error(f"搜索信用卡失败: {str(e)}")
        return []

def format_knowledge_base(cards: List[Dict]) -> str:
    """格式化知识库信息"""
    if not cards:
        return ""
    
    knowledge = "信用卡知识库：\n\n"
    for card in cards:
        knowledge += f"【{card['bank_name']} - {card['card_name']}】\n"
        knowledge += f"卡片等级：{card['card_level']}\n"
        if card['annual_fee']:
            knowledge += f"年费政策：{card['annual_fee']}\n"
        if card['credit_limit']:
            knowledge += f"信用额度：{card['credit_limit']}\n"
        if card['benefits']:
            knowledge += f"主要权益：{card['benefits']}\n"
        if card['requirements']:
            knowledge += f"申请条件：{card['requirements']}\n"
        knowledge += "\n"
    
    return knowledge

@router.post("/chat")
async def chat_with_assistant(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """与AI助手进行对话"""
    try:
        logger.info(f"收到聊天请求 - 用户ID: {current_user['id']}, 消息: {chat_message.message}")
        
        # 从知识库搜索相关信息
        logger.info("开始搜索知识库...")
        cards = search_credit_cards(chat_message.message)
        logger.info(f"搜索到 {len(cards)} 条信用卡信息")
        knowledge = format_knowledge_base(cards)
        
        # 初始化 DeepSeek 适配器
        logger.info("初始化 DeepSeek 适配器...")
        deepseek = DeepSeekAdapter()
        
        try:
            # 构建系统提示词
            system_prompt = """你是一个专业的信用卡助手，请基于提供的知识库信息回答用户的问题。
如果知识库中没有相关信息，请明确告知用户。
请用专业、友好的语气回答，并确保回答准确、完整。"""
            
            # 构建用户提示词
            user_prompt = f"""知识库信息：
{knowledge}

用户问题：{chat_message.message}"""
            
            logger.info("开始调用 DeepSeek API...")
            # 调用 DeepSeek API 获取回答
            response = await deepseek.chat_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            logger.info("DeepSeek API 调用成功")
            
            # 保存聊天记录
            logger.info("保存聊天记录...")
            save_chat_history(current_user["id"], chat_message.message, response)
            
            logger.info("成功生成回答，准备返回响应")
            return {
                "response": response,
                "status": "success",
                "context": {
                    "type": "deepseek_response",
                    "knowledge_used": bool(knowledge)
                }
            }
        finally:
            # 确保关闭 DeepSeek 客户端
            logger.info("关闭 DeepSeek 客户端")
            await deepseek.close()
            
    except Exception as e:
        logger.error(f"处理聊天请求失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/{chat_id}")
async def delete_chat_message(
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除聊天记录"""
    try:
        logger.info(f"删除聊天记录 - 用户ID: {current_user['id']}, 聊天ID: {chat_id}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 软删除聊天记录
        cursor.execute(
            "UPDATE chat_history SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s",
            (chat_id, current_user["id"])
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="聊天记录不存在或无权删除")
            
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("聊天记录删除成功")
        return {"message": "聊天记录删除成功"}
    except Exception as e:
        logger.error(f"删除聊天记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history_endpoint(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """获取聊天历史记录"""
    try:
        logger.info(f"获取用户 {current_user['id']} 的聊天历史记录")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 只获取未删除的记录
        cursor.execute(
            """
            SELECT id, message, response, created_at 
            FROM chat_history 
            WHERE user_id = %s AND deleted_at IS NULL 
            ORDER BY created_at DESC 
            LIMIT %s
            """,
            (current_user["id"], limit)
        )
        
        history = cursor.fetchall()
        logger.info(f"找到 {len(history)} 条历史记录")
        
        formatted_history = []
        for msg in history:
            formatted_history.extend([
                {
                    "id": msg["id"],
                    "role": "user",
                    "content": msg["message"],
                    "created_at": msg["created_at"].isoformat()
                },
                {
                    "id": msg["id"],
                    "role": "assistant",
                    "content": msg["response"],
                    "created_at": msg["created_at"].isoformat()
                }
            ])
            
        cursor.close()
        conn.close()
        return formatted_history
    except Exception as e:
        logger.error(f"获取聊天历史记录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 