"""
测试基于大模型的数据搜集模块
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()

from backend.crawler.llm_crawler import LLMCrawler

def test_llm_crawler():
    """测试基于大模型的数据搜集模块"""
    try:
        # 初始化爬虫
        crawler = LLMCrawler()
        
        # 开始爬取
        crawler.crawl_all_banks()
            
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 设置日志级别和格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    # 添加分隔线
    print("\n" + "="*80 + "\n")
    print("开始信用卡数据采集任务")
    print("\n" + "="*80 + "\n")
    
    # 运行测试
    test_llm_crawler()
    
    # 添加分隔线
    print("\n" + "="*80 + "\n")
    print("信用卡数据采集任务结束")
    print("\n" + "="*80 + "\n") 