from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging
from database.db import get_db_connection
from .auth import get_current_user

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

class CreditCard(BaseModel):
    id: Optional[int] = None
    bank: str
    name: str
    level: Optional[str] = None
    annual_fee: Optional[str] = None
    benefits: Optional[Dict[str, str]] = Field(default_factory=dict)
    requirements: Optional[Dict[str, str]] = Field(default_factory=dict)
    points_rule: Optional[str] = None
    credit_limit: Optional[str] = None
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

@router.get("/cards", response_model=List[CreditCard])
async def get_credit_cards(
    bank: Optional[str] = Query(None, description="银行名称"),
    level: Optional[str] = Query(None, description="卡片等级"),
    current_user: dict = Depends(get_current_user)
):
    """获取信用卡列表"""
    conn = None
    cursor = None
    try:
        logger.debug("开始获取信用卡列表")
        logger.debug(f"认证用户信息: {current_user}")
        logger.debug(f"请求参数: bank={bank}, level={level}")
        
        conn = get_db_connection()
        logger.debug("数据库连接成功")
        cursor = conn.cursor(dictionary=True)
        logger.debug("游标创建成功")
        
        # 构建基本查询
        query = "SELECT * FROM credit_cards"
        params = []
        
        # 添加筛选条件
        conditions = []
        if bank:
            conditions.append("bank = %s")
            params.append(bank)
        if level:
            conditions.append("level = %s")
            params.append(level)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        logger.debug(f"执行SQL查询: {query}")
        logger.debug(f"查询参数: {params}")
        
        cursor.execute(query, params)
        cards = cursor.fetchall()
        logger.debug(f"查询到 {len(cards)} 张信用卡")
        
        if not cards:
            logger.debug("没有找到任何信用卡")
            return []
        
        result = []
        for card in cards:
            try:
                # 处理JSON字段
                if card['benefits']:
                    try:
                        card['benefits'] = json.loads(card['benefits'])
                    except json.JSONDecodeError:
                        card['benefits'] = {}
                else:
                    card['benefits'] = {}
                
                if card['requirements']:
                    try:
                        card['requirements'] = json.loads(card['requirements'])
                    except json.JSONDecodeError:
                        card['requirements'] = {}
                else:
                    card['requirements'] = {}
                
                credit_card = CreditCard(**card)
                result.append(credit_card)
                logger.debug(f"成功处理卡片: {credit_card.name}")
                
            except Exception as e:
                logger.error(f"处理卡片时出错: {str(e)}, card: {card}")
                continue
        
        logger.debug(f"成功处理 {len(result)} 张信用卡")
        return result
        
    except Exception as e:
        logger.error(f"获取信用卡列表错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.get("/cards/{card_id}", response_model=CreditCard)
async def get_credit_card(
    card_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取特定信用卡的详细信息"""
    conn = None
    cursor = None
    try:
        logger.debug(f"开始获取信用卡详情: {card_id}")
        logger.debug(f"当前用户: {current_user['username']}")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM credit_cards WHERE id = %s", (card_id,))
        card = cursor.fetchone()
        
        if not card:
            logger.warning(f"未找到信用卡: {card_id}")
            raise HTTPException(status_code=404, detail="信用卡不存在")
        
        logger.debug(f"找到信用卡: {card['name']}")
        
        # 处理JSON字段
        if card['benefits']:
            try:
                card['benefits'] = json.loads(card['benefits'])
            except json.JSONDecodeError as e:
                logger.error(f"解析benefits失败: {e}, 原始数据: {card['benefits']}")
                card['benefits'] = {}
        else:
            card['benefits'] = {}
        
        if card['requirements']:
            try:
                card['requirements'] = json.loads(card['requirements'])
            except json.JSONDecodeError as e:
                logger.error(f"解析requirements失败: {e}, 原始数据: {card['requirements']}")
                card['requirements'] = {}
        else:
            card['requirements'] = {}
        
        credit_card = CreditCard(**card)
        logger.debug(f"成功处理信用卡详情: {credit_card.name}")
        return credit_card
        
    except Exception as e:
        logger.error(f"获取信用卡详情错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 