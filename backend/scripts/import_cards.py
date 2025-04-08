import json
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent

# 导入数据库连接函数
import sys
sys.path.append(str(project_root))
from backend.database.db import get_db_connection

def import_credit_cards(json_file_path):
    try:
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            credit_cards = json.load(f)

        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
            # 确保所有字段都存在，如果不存在则使用默认值
            card_data = {
                'bank': card.get('bank', ''),
                'name': card.get('name', ''),
                'timestamp': card.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'level': card.get('level', ''),
                'annual_fee': card.get('annual_fee', ''),
                'benefits': json.dumps(card.get('benefits', {}), ensure_ascii=False),
                'requirements': json.dumps(card.get('requirements', {}), ensure_ascii=False),
                'points_rule': card.get('points_rule', ''),
                'credit_limit': card.get('credit_limit', '')
            }

            try:
                values = (
                    card_data['bank'],
                    card_data['name'],
                    datetime.strptime(card_data['timestamp'], '%Y-%m-%d %H:%M:%S'),
                    card_data['level'],
                    card_data['annual_fee'],
                    card_data['benefits'],
                    card_data['requirements'],
                    card_data['points_rule'],
                    card_data['credit_limit']
                )
                cursor.execute(insert_query, values)
                print(f"成功导入: {card_data['bank']} - {card_data['name']}")
            except Exception as e:
                print(f"导入失败: {card_data['bank']} - {card_data['name']}, 错误: {str(e)}")
                continue

        # 提交事务
        conn.commit()
        print(f"\n总共成功导入 {len(credit_cards)} 条信用卡数据")

    except Exception as e:
        print(f"导入数据时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    json_file_path = os.path.join(project_root, 'results/credit_cards_detail_20250408_025432.json')
    import_credit_cards(json_file_path) 