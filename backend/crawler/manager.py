"""
爬虫管理器
管理所有银行的爬虫实例
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from .icbc_crawler import ICBCCrawler
from .cmb_crawler import CMBCrawler
from .boc_crawler import BOCCrawler

class CrawlerManager:
    """爬虫管理器类"""
    
    def __init__(self):
        """初始化爬虫管理器"""
        self.crawlers = {
            "工商银行": ICBCCrawler(),
            "招商银行": CMBCrawler(),
            "中国银行": BOCCrawler()
        }
        
        # 确保数据目录存在
        self.data_dir = "data/cards"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def crawl_all(self) -> List[Dict]:
        """抓取所有银行的信用卡信息"""
        all_cards = []
        
        # 遍历所有爬虫
        for bank_name, crawler in self.crawlers.items():
            try:
                print(f"\n开始抓取{bank_name}信用卡信息...")
                
                # 获取信用卡列表
                cards = crawler.get_card_list()
                print(f"获取到 {len(cards)} 张信用卡")
                
                # 获取每张卡的详细信息
                for card in cards:
                    try:
                        if card_id := card.get("card_id"):
                            detail = crawler.get_card_detail(card_id)
                            card.update(detail)
                    except Exception as e:
                        print(f"获取卡片详情失败: {str(e)}")
                        continue
                
                all_cards.extend(cards)
                
            except Exception as e:
                print(f"{bank_name}爬虫运行失败: {str(e)}")
                continue
        
        # 保存结果
        if all_cards:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cards_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(all_cards, f, ensure_ascii=False, indent=2)
            print(f"\n数据已保存到: {filepath}")
        
        return all_cards
    
    async def crawl_all_cards(self) -> List[Dict]:
        """并行爬取所有银行的信用卡信息"""
        tasks = []
        for bank, crawler in self.crawlers.items():
            task = asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._crawl_bank_cards,
                bank,
                crawler
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        all_cards = []
        for bank_cards in results:
            all_cards.extend(bank_cards)
        
        return all_cards
    
    def _crawl_bank_cards(self, bank: str, crawler) -> List[Dict]:
        """爬取单个银行的信用卡信息"""
        try:
            # 获取信用卡列表
            cards = crawler.get_card_list()
            
            # 获取每张卡的详细信息
            for card in cards:
                detail = crawler.get_card_detail(card["url"])
                card.update(detail)
            
            return cards
            
        except Exception as e:
            print(f"爬取{bank}信用卡信息失败: {str(e)}")
            return []
    
    async def crawl_specific_bank(self, bank: str) -> List[Dict]:
        """爬取指定银行的信用卡信息"""
        if bank not in self.crawlers:
            return []
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._crawl_bank_cards,
            bank,
            self.crawlers[bank]
        )
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown()
        for crawler in self.crawlers.values():
            del crawler 