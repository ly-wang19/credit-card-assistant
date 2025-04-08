from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

router = APIRouter()

class AnnualFee(BaseModel):
    first_year: str
    regular: str
    waiver_condition: str

class PointsRule(BaseModel):
    domestic: str
    overseas: str
    special: str

class ApplicationCondition(BaseModel):
    income: str
    credit_score: str
    age: str

class CreditCard(BaseModel):
    id: Optional[int] = None
    name: str
    bank: str
    annual_fee: Optional[AnnualFee] = None
    points_rule: Optional[PointsRule] = None
    benefits: Optional[List[str]] = None
    card_type: Optional[str] = None
    credit_level: Optional[str] = None
    foreign_transaction_fee: Optional[str] = None
    card_organization: Optional[str] = None
    application_condition: Optional[ApplicationCondition] = None

@router.get("/cards", response_model=List[CreditCard])
async def get_credit_cards(
    bank: Optional[str] = Query(None, description="银行名称"),
    card_type: Optional[str] = Query(None, description="卡片类型"),
    credit_level: Optional[str] = Query(None, description="信用等级")
):
    """获取信用卡列表"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM credit_cards WHERE 1=1"
        params = []
        
        if bank:
            query += " AND bank = %s"
            params.append(bank)
            
        if card_type:
            query += " AND card_type = %s"
            params.append(card_type)
            
        if credit_level:
            query += " AND credit_level = %s"
            params.append(credit_level)
            
        cursor.execute(query, params)
        cards = cursor.fetchall()
        
        # 将JSON字符串转换为字典
        for card in cards:
            try:
                if card['annual_fee']:
                    card['annual_fee'] = json.loads(card['annual_fee'])
                if card['points_rule']:
                    card['points_rule'] = json.loads(card['points_rule'])
                if card['benefits']:
                    card['benefits'] = json.loads(card['benefits'])
                if card['application_condition']:
                    card['application_condition'] = json.loads(card['application_condition'])
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}, card: {card['name']}")
                continue
        
        return cards
        
    except Exception as e:
        print(f"获取信用卡列表错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.get("/cards/{card_id}", response_model=CreditCard)
async def get_credit_card(card_id: int):
    """获取特定信用卡的详细信息"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM credit_cards WHERE id = %s", (card_id,))
        card = cursor.fetchone()
        
        if not card:
            raise HTTPException(status_code=404, detail="信用卡不存在")
            
        # 将JSON字符串转换为字典
        try:
            if card['annual_fee']:
                card['annual_fee'] = json.loads(card['annual_fee'])
            if card['points_rule']:
                card['points_rule'] = json.loads(card['points_rule'])
            if card['benefits']:
                card['benefits'] = json.loads(card['benefits'])
            if card['application_condition']:
                card['application_condition'] = json.loads(card['application_condition'])
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}, card: {card['name']}")
            
        return card
        
    except Exception as e:
        print(f"获取信用卡详情错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close() 