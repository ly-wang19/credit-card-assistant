import os
import json
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 数据库配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USERNAME', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_DATABASE', 'credit_card_db')
}

# 示例数据
sample_cards = [
    {
        "name": "招商银行经典白金卡",
        "bank": "招商银行",
        "card_type": "信用卡",
        "credit_level": "白金卡",
        "card_organization": "银联+Mastercard",
        "annual_fee": json.dumps({
            "first_year": "免年费",
            "regular": "主卡300元/年",
            "waiver_condition": "消费6次免次年年费"
        }),
        "points_rule": json.dumps({
            "default": "消费1元=1积分",
            "special": ["境外消费2倍积分", "网上支付1.5倍积分"],
            "expiration": "积分3年有效"
        }),
        "benefits": json.dumps([
            "机场贵宾厅2次/年",
            "高尔夫球场服务",
            "境外医疗援助",
            "航班延误险"
        ]),
        "application_condition": json.dumps({
            "income": "年收入8万以上",
            "credit_score": "良好",
            "age": "年满18周岁"
        }),
        "foreign_transaction_fee": "1.5%",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "name": "中信银行无限卡",
        "bank": "中信银行",
        "card_type": "信用卡",
        "credit_level": "无限卡",
        "card_organization": "Visa",
        "annual_fee": json.dumps({
            "first_year": "免年费",
            "regular": "主卡3000元/年",
            "waiver_condition": "年消费30万免次年年费"
        }),
        "points_rule": json.dumps({
            "default": "消费1元=2积分",
            "special": ["境外消费3倍积分", "指定商户5倍积分"],
            "expiration": "积分5年有效"
        }),
        "benefits": json.dumps([
            "全球机场贵宾厅无限次",
            "高尔夫球场无限次",
            "专属管家服务",
            "全球医疗援助"
        ]),
        "application_condition": json.dumps({
            "income": "年收入50万以上",
            "credit_score": "优秀",
            "age": "年满25周岁"
        }),
        "foreign_transaction_fee": "2%",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

def import_sample_data():
    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 开始事务
        conn.start_transaction()
        
        # 插入信用卡数据
        insert_query = """
        INSERT INTO credit_cards (
            name, bank, card_type, credit_level, card_organization,
            annual_fee, points_rule, benefits, application_condition,
            foreign_transaction_fee, created_at, updated_at
        ) VALUES (
            %(name)s, %(bank)s, %(card_type)s, %(credit_level)s, %(card_organization)s,
            %(annual_fee)s, %(points_rule)s, %(benefits)s, %(application_condition)s,
            %(foreign_transaction_fee)s, %(created_at)s, %(updated_at)s
        )
        """
        
        for card in sample_cards:
            cursor.execute(insert_query, card)
            print(f"成功插入信用卡数据: {card['name']}")
        
        # 提交事务
        conn.commit()
        print("所有数据导入成功！")
        
    except mysql.connector.Error as err:
        # 发生错误时回滚事务
        print(f"发生错误: {err}")
        conn.rollback()
        raise
    
    finally:
        # 关闭数据库连接
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    import_sample_data() 