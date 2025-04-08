#!/usr/bin/env python3
import json
import logging
import sys
import os
from typing import List, Dict, Any
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# 添加父目录到Python路径以导入项目模块
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, CreditCard
from config import Settings

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
        'database': 'credit_card_db'
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

def import_credit_cards(json_file_path: str) -> None:
    """从JSON文件导入信用卡数据到MySQL数据库"""
    if not os.path.exists(json_file_path):
        logging.error(f"文件不存在: {json_file_path}")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 获取credit_cards数组
            credit_cards = data.get('credit_cards', [])
    except json.JSONDecodeError as e:
        logging.error(f"JSON解析错误: {str(e)}")
        return
    except Exception as e:
        logging.error(f"读取文件时发生错误: {str(e)}")
        return

    if not isinstance(credit_cards, list):
        logging.error("JSON数据必须是信用卡对象的列表")
        return

    connection = None
    try:
        connection = mysql.connector.connect(**get_db_config())
        cursor = connection.cursor()
        
        # 准备SQL语句
        insert_query = """
        INSERT INTO credit_cards (
            name, bank, annual_fee, points_rule, benefits,
            card_type, credit_level, foreign_transaction_fee,
            card_organization, application_condition
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        success_count = 0
        for card in credit_cards:
            try:
                values = (
                    card.get('name', ''),
                    card.get('bank', ''),
                    format_annual_fee(card.get('annual_fee', {})),
                    format_points_rule(card.get('points_rule', {})),
                    format_benefits(card.get('benefits', [])),
                    card.get('card_type', ''),
                    card.get('credit_level', ''),
                    card.get('foreign_transaction_fee', ''),
                    card.get('card_organization', ''),
                    format_application_condition(card.get('application_condition', {}))
                )
                cursor.execute(insert_query, values)
                success_count += 1
                logging.info(f"成功导入卡片: {card.get('name')}")
            except Error as e:
                logging.error(f"插入信用卡数据时发生错误: {str(e)}")
                logging.error(f"失败的数据: {card}")
                continue

        connection.commit()
        logging.info(f"成功导入 {success_count} 张信用卡")

    except Error as e:
        logging.error(f"数据库连接错误: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("数据库连接已关闭")

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python import_credit_cards.py <json文件路径>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    import_credit_cards(json_file_path)
    main() 