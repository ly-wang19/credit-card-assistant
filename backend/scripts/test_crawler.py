"""
测试信用卡爬虫
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.crawler.icbc_crawler import ICBCCrawler

def test_icbc_crawler():
    """测试工商银行信用卡爬虫"""
    try:
        crawler = ICBCCrawler()
        cards = crawler.crawl_all_cards()
        
        if cards:
            print(f"\n成功抓取 {len(cards)} 张信用卡信息")
            
            # 打印第一张卡片的详细信息作为示例
            if len(cards) > 0:
                print("\n第一张卡片信息示例:")
                card = cards[0]
                print(f"名称: {card.get('name')}")
                print(f"类型: {card.get('type')}")
                print(f"年费: {card.get('annual_fee')}")
                
                print("\n权益信息:")
                for title, desc in card.get('benefits', {}).items():
                    print(f"  {title}: {desc}")
                
                print("\n申请条件:")
                for title, content in card.get('requirements', {}).items():
                    print(f"  {title}: {content}")
        else:
            print("未获取到任何信用卡信息")
            
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    test_icbc_crawler() 