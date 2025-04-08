import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
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

class MessageResponse(BaseModel):
    id: Optional[int]
    role: str
    content: str
    created_at: Optional[datetime]

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

def get_active_conversation(user_id: int, conn) -> int:
    """获取或创建活动会话"""
    cursor = conn.cursor(dictionary=True)
    
    # 查找最新的会话
    cursor.execute(
        "SELECT id FROM conversations WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    result = cursor.fetchone()
    
    if result:
        conversation_id = result['id']
    else:
        # 创建新会话
        cursor.execute(
            "INSERT INTO conversations (user_id) VALUES (%s)",
            (user_id,)
        )
        conn.commit()
        conversation_id = cursor.lastrowid
    
    cursor.close()
    return conversation_id

def save_message(conn, conversation_id: int, role: str, content: str) -> int:
    """保存消息"""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (conversation_id, role, content) VALUES (%s, %s, %s)",
        (conversation_id, role, content)
    )
    message_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return message_id

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
        conn = get_db_connection()
        
        # 获取或创建会话
        conversation_id = get_active_conversation(current_user['id'], conn)
        
        # 保存用户消息
        user_message_id = save_message(conn, conversation_id, 'user', chat_message.message)
        
        # 从知识库搜索相关信息
        cards = search_credit_cards(chat_message.message)
        knowledge = format_knowledge_base(cards)
        
        # 初始化 DeepSeek 适配器
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
            
            # 调用 DeepSeek API 获取回答
            response = await deepseek.chat_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            # 保存AI回复
            assistant_message_id = save_message(conn, conversation_id, 'assistant', response)
            
            return {
                "response": response,
                "message_id": assistant_message_id,
                "status": "success"
            }
        finally:
            await deepseek.close()
            
    except Exception as e:
        logger.error(f"处理聊天请求失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/chat/history")
async def get_chat_history_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """获取聊天历史记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取最新会话的消息
        cursor.execute("""
            SELECT m.* FROM chat_messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = %s
            ORDER BY m.created_at ASC
        """, (current_user['id'],))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "id": msg['id'],
                "role": msg['role'],
                "content": msg['content'],
                "created_at": msg['created_at']
            }
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取聊天历史失败")

@router.post("/chat/new")
async def create_new_conversation(
    current_user: dict = Depends(get_current_user)
):
    """创建新会话"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建新会话
        cursor.execute(
            "INSERT INTO conversations (user_id) VALUES (%s)",
            (current_user['id'],)
        )
        conn.commit()
        
        # 添加欢迎消息
        conversation_id = cursor.lastrowid
        welcome_message = """您好！我是AI信用卡助手，我可以帮您：
1. 推荐最适合您的信用卡
2. 解答信用卡相关问题
3. 对比不同信用卡的权益
请告诉我您的需求。"""
        
        save_message(conn, conversation_id, 'assistant', welcome_message)
        
        cursor.close()
        conn.close()
        
        return {"message": "新会话已创建"}
    except Exception as e:
        logger.error(f"创建新会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建新会话失败")

@router.delete("/chat/history")
async def clear_chat_history(
    current_user: dict = Depends(get_current_user)
):
    """清空聊天历史"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除用户的所有会话（会级联删除消息）
        cursor.execute(
            "DELETE FROM conversations WHERE user_id = %s",
            (current_user['id'],)
        )
        conn.commit()
        
        # 创建新会话并添加欢迎消息
        cursor.execute(
            "INSERT INTO conversations (user_id) VALUES (%s)",
            (current_user['id'],)
        )
        conn.commit()
        
        conversation_id = cursor.lastrowid
        welcome_message = """您好！我是AI信用卡助手，我可以帮您：
1. 推荐最适合您的信用卡
2. 解答信用卡相关问题
3. 对比不同信用卡的权益
请告诉我您的需求。"""
        
        save_message(conn, conversation_id, 'assistant', welcome_message)
        
        cursor.close()
        conn.close()
        
        return {"message": "聊天历史已清空"}
    except Exception as e:
        logger.error(f"清空聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="清空聊天历史失败")

@router.delete("/chat/message/{message_id}")
async def delete_message_endpoint(
    message_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除单条消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证消息所有权
        cursor.execute("""
            SELECT m.id FROM chat_messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE m.id = %s AND c.user_id = %s
        """, (message_id, current_user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="消息不存在或无权删除")
        
        # 删除消息
        cursor.execute("DELETE FROM chat_messages WHERE id = %s", (message_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "消息已删除"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"删除消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除消息失败") 