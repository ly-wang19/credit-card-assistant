#!/usr/bin/env python3
"""
信用卡爬虫脚本
运行所有银行的信用卡爬虫
"""

from backend.crawler.manager import CrawlerManager

def main():
    """主函数"""
    try:
        print("开始爬取所有银行的信用卡信息...")
        manager = CrawlerManager()
        cards = manager.crawl_all()
        print(f"\n总共获取到 {len(cards)} 张信用卡信息")
        
    except Exception as e:
        print(f"爬取过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 