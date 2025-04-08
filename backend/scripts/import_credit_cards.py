#!/usr/bin/env python3
import json
import logging
import sys
import os
from typing import List, Dict, Any
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CreditCard
from config import Settings
from backend.database.db import get_db_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_credit_cards.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_config() -> Dict[str, str]:
    """获取数据库配置"""
    return {
        'host': 'localhost',
        'user': 'root',
        'password': '1996129.yin',
        'database': 'credit_card_assistant'
    }

def format_annual_fee(annual_fee: Dict) -> str:
    """格式化年费信息"""
    if isinstance(annual_fee, dict):
        parts = []
        if 'first_year' in annual_fee:
            parts.append(f"首年{annual_fee['first_year']}")
        if 'regular' in annual_fee:
            parts.append(annual_fee['regular'])
        if 'waiver_condition' in annual_fee:
            parts.append(f"({annual_fee['waiver_condition']})")
        return '，'.join(parts)
    return str(annual_fee)

def format_points_rule(points_rule: Dict) -> str:
    """格式化积分规则"""
    if isinstance(points_rule, dict):
        return '；'.join(f"{k}：{v}" for k, v in points_rule.items())
    return str(points_rule)

def format_benefits(benefits: List) -> str:
    """格式化权益信息"""
    if isinstance(benefits, list):
        return '，'.join(benefits)
    return str(benefits)

def format_application_condition(condition: Dict) -> str:
    """格式化申请条件"""
    if isinstance(condition, dict):
        return '，'.join(f"{v}" for v in condition.values())
    return str(condition)

def import_credit_cards(json_file_path):
    try:
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            credit_cards = json.load(f)

        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建信用卡表（如果不存在）
        with open(os.path.join(project_root, 'backend/database/credit_cards.sql'), 'r', encoding='utf-8') as f:
            sql_create_table = f.read()
            cursor.execute(sql_create_table)

        # 准备插入语句
        insert_query = """
        INSERT INTO credit_cards 
        (bank, name, timestamp, level, annual_fee, benefits, requirements, points_rule, credit_limit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        timestamp = VALUES(timestamp),
        level = VALUES(level),
        annual_fee = VALUES(annual_fee),
        benefits = VALUES(benefits),
        requirements = VALUES(requirements),
        points_rule = VALUES(points_rule),
        credit_limit = VALUES(credit_limit)
        """

        # 插入数据
        for card in credit_cards:
            values = (
                card['bank'],
                card['name'],
                datetime.strptime(card['timestamp'], '%Y-%m-%d %H:%M:%S'),
                card['level'],
                card['annual_fee'],
                json.dumps(card['benefits'], ensure_ascii=False),
                json.dumps(card['requirements'], ensure_ascii=False),
                card['points_rule'],
                card['credit_limit']
            )
            cursor.execute(insert_query, values)

        # 提交事务
        conn.commit()
        print(f"成功导入 {len(credit_cards)} 条信用卡数据")

    except Exception as e:
        print(f"导入数据时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_database_connection():
    """创建数据库连接"""
    settings = Settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal()

def create_tables(engine):
    """创建数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表时出错: {e}")
        raise

def import_sample_data(session):
    """导入示例信用卡数据"""
    try:
        # 示例信用卡数据
        sample_cards = [
            {
                "name": "招商银行经典白金卡",
                "bank": "招商银行",
                "card_type": "白金卡",
                "annual_fee": "主卡300元/年",
                "benefits": "1. 航空意外保险\n2. 高尔夫特权\n3. 机场贵宾厅",
                "requirements": "年收入10万以上",
                "points_rules": "消费1元累计1积分",
                "card_level": "白金",
                "image_url": "https://example.com/card1.jpg"
            },
            {
                "name": "中信银行颜卡",
                "bank": "中信银行",
                "card_type": "标准卡",
                "annual_fee": "主卡免年费",
                "benefits": "1. 网购返现\n2. 视频会员特权",
                "requirements": "年收入3万以上",
                "points_rules": "线上消费1元累计2积分，线下1元1积分",
                "card_level": "金卡",
                "image_url": "https://example.com/card2.jpg"
            }
        ]

        for card_data in sample_cards:
            card = CreditCard(**card_data)
            session.add(card)
        
        session.commit()
        logger.info(f"成功导入 {len(sample_cards)} 张信用卡数据")

    except Exception as e:
        session.rollback()
        logger.error(f"导入数据时出错: {e}")
        raise

def main():
    """主函数"""
    try:
        engine, session = create_database_connection()
        create_tables(engine)
        import_sample_data(session)
        logger.info("数据导入完成")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    json_file_path = os.path.join(project_root, 'results/credit_cards_detail_20250408_025432.json')
    import_credit_cards(json_file_path)
    main() 