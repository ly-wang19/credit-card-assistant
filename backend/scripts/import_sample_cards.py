import sys
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.credit_card import Base, CreditCard
from config import settings

# 使用settings中的DATABASE_URL
DATABASE_URL = settings.DATABASE_URL

def create_sample_cards():
    # 创建示例信用卡数据
    return [
        {
            "name": "招商银行经典白金卡",
            "bank": "招商银行",
            "card_type": "白金卡",
            "credit_level": "中高端",
            "card_organization": "银联+Visa",
            "annual_fee": json.dumps({
                "first_year": "免年费",
                "subsequent_years": "消费满6次免年费，否则300元/年"
            }, ensure_ascii=False),
            "points_rule": json.dumps({
                "国内消费": "每消费1元累积1分",
                "境外消费": "每消费1元累积2分",
                "积分有效期": "3年"
            }, ensure_ascii=False),
            "benefits": json.dumps([
                "航空里程兑换",
                "机场贵宾厅",
                "高尔夫特权",
                "境外医疗保险"
            ], ensure_ascii=False),
            "application_condition": json.dumps({
                "年龄要求": "18-65周岁",
                "收入要求": "年收入8万元以上",
                "信用记录": "信用记录良好"
            }, ensure_ascii=False),
            "foreign_transaction_fee": "1.5%"
        },
        {
            "name": "中信银行无限卡",
            "bank": "中信银行",
            "card_type": "无限卡",
            "credit_level": "顶级",
            "card_organization": "Visa",
            "annual_fee": json.dumps({
                "first_year": "2000元",
                "subsequent_years": "2000元/年"
            }, ensure_ascii=False),
            "points_rule": json.dumps({
                "国内消费": "每消费1元累积2分",
                "境外消费": "每消费1元累积3分",
                "积分有效期": "5年"
            }, ensure_ascii=False),
            "benefits": json.dumps([
                "全球机场贵宾厅无限次",
                "高端酒店特权",
                "全球礼宾服务",
                "高额出行保险"
            ], ensure_ascii=False),
            "application_condition": json.dumps({
                "年龄要求": "25-65周岁",
                "收入要求": "年收入50万元以上",
                "资产要求": "金融资产300万元以上"
            }, ensure_ascii=False),
            "foreign_transaction_fee": "免收"
        }
    ]

def main():
    print("开始导入示例信用卡数据...")
    try:
        # 创建数据库引擎
        print(f"使用数据库URL: {DATABASE_URL}")
        engine = create_engine(DATABASE_URL, echo=True)
        
        # 创建所有表
        Base.metadata.create_all(engine)
        print("数据库表已创建")
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 检查是否已有数据
            existing_count = session.query(CreditCard).count()
            if existing_count > 0:
                print(f"数据库中已有 {existing_count} 张信用卡，跳过导入")
                return
            
            # 获取示例数据
            sample_cards = create_sample_cards()
            print(f"准备导入 {len(sample_cards)} 张信用卡数据")
            
            # 插入数据
            for card_data in sample_cards:
                try:
                    # 检查是否已存在相同名称和发卡行的卡
                    existing_card = session.query(CreditCard).filter_by(
                        name=card_data['name'],
                        bank=card_data['bank']
                    ).first()
                    
                    if existing_card:
                        print(f"跳过已存在的卡片: {card_data['name']}")
                        continue
                    
                    card = CreditCard(**card_data)
                    session.add(card)
                    print(f"添加卡片: {card_data['name']}")
                except Exception as e:
                    print(f"添加卡片 {card_data['name']} 时出错: {str(e)}")
                    raise
            
            # 提交事务
            session.commit()
            print("成功导入示例信用卡数据！")
            
            # 验证数据
            cards = session.query(CreditCard).all()
            print(f"数据库中现有 {len(cards)} 张信用卡")
            for card in cards:
                print(f"- {card.name} ({card.bank})")
            
        except Exception as e:
            print(f"导入数据时发生错误: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 