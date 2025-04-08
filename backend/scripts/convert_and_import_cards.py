import json
import mysql.connector
from typing import Dict, Any

def get_db_config() -> Dict[str, str]:
    """获取数据库配置"""
    return {
        'host': 'localhost',
        'user': 'root',
        'password': '1996129.yin',
        'database': 'credit_card_assistant'
    }

def convert_card_data(card: Dict[str, Any]) -> Dict[str, Any]:
    """转换信用卡数据格式"""
    return {
        "id": card.get("id"),
        "name": card.get("name"),
        "bank": card.get("bank"),
        "annual_fee": {
            "first_year": card.get("first_year_fee", "免年费"),
            "regular": card.get("annual_fee", ""),
            "waiver_condition": card.get("fee_waiver", "")
        },
        "points_rule": {
            "domestic": card.get("points_rule", ""),
            "overseas": card.get("overseas_points_rule", ""),
            "special": card.get("special_points_rule", "")
        },
        "benefits": card.get("benefits", "").split("，") if isinstance(card.get("benefits"), str) else [],
        "card_type": card.get("card_type"),
        "credit_level": card.get("credit_level"),
        "foreign_transaction_fee": card.get("foreign_transaction_fee"),
        "card_organization": card.get("card_organization"),
        "application_condition": {
            "income": card.get("income_requirement", ""),
            "credit_score": "信用记录良好",
            "age": "年满18周岁"
        }
    }

def format_card_for_db(card: Dict[str, Any]) -> Dict[str, str]:
    """格式化信用卡数据用于数据库存储"""
    return {
        "name": card["name"],
        "bank": card["bank"],
        "annual_fee": json.dumps(card["annual_fee"], ensure_ascii=False),
        "points_rule": json.dumps(card["points_rule"], ensure_ascii=False),
        "benefits": json.dumps(card["benefits"], ensure_ascii=False),
        "card_type": card["card_type"],
        "credit_level": card["credit_level"],
        "foreign_transaction_fee": card["foreign_transaction_fee"],
        "card_organization": card["card_organization"],
        "application_condition": json.dumps(card["application_condition"], ensure_ascii=False)
    }

def import_cards(cards_data: list) -> None:
    """导入信用卡数据到数据库"""
    connection = None
    try:
        connection = mysql.connector.connect(**get_db_config())
        cursor = connection.cursor()

        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # 清空现有数据
        cursor.execute("TRUNCATE TABLE credit_cards")
        
        # 准备SQL语句
        insert_query = """
        INSERT INTO credit_cards (
            name, bank, annual_fee, points_rule, benefits,
            card_type, credit_level, foreign_transaction_fee,
            card_organization, application_condition
        ) VALUES (
            %(name)s, %(bank)s, %(annual_fee)s, %(points_rule)s, %(benefits)s,
            %(card_type)s, %(credit_level)s, %(foreign_transaction_fee)s,
            %(card_organization)s, %(application_condition)s
        )
        """
        
        for card in cards_data:
            converted_card = convert_card_data(card)
            db_card = format_card_for_db(converted_card)
            cursor.execute(insert_query, db_card)
            print(f"成功导入卡片: {db_card['name']}")

        connection.commit()
        
        # 重新启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
        print(f"成功导入 {len(cards_data)} 张信用卡")

    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # 读取原始数据
    with open("results/credit_cards_detail_20250408_025432.json", "r", encoding="utf-8") as f:
        original_data = json.load(f)
    
    # 导入数据
    import_cards(original_data) 