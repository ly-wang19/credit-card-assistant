"""
中国银行信用卡爬虫
实现中国银行信用卡信息的抓取
"""

from typing import Dict, List
import json
import requests
from .base_crawler import BaseCrawler

class BOCCrawler(BaseCrawler):
    """中国银行信用卡爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.boc.cn"
        self.card_list_url = f"{self.base_url}/bcservice/api/credit-card/list"
        self.card_detail_url = f"{self.base_url}/bcservice/api/credit-card/detail"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.boc.cn",
            "Referer": "https://www.boc.cn/bcservice/credit-card/",
            "X-Requested-With": "XMLHttpRequest"
        }
    
    def get_card_list(self) -> List[Dict]:
        """获取信用卡列表"""
        try:
            print("正在访问中国银行信用卡列表API...")
            response = requests.post(
                self.card_list_url,
                headers=self.headers,
                json={
                    "pageSize": 50,
                    "pageNum": 1,
                    "cardType": "ALL"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"API请求失败: {response.status_code}")
                return []
            
            data = response.json()
            if not data.get("success"):
                print(f"获取数据失败: {data.get('message')}")
                return []
            
            cards = []
            for item in data.get("data", {}).get("list", []):
                try:
                    card = {
                        "bank": "中国银行",
                        "name": item.get("cardName", ""),
                        "type": item.get("cardType", ""),
                        "image": item.get("cardImage", ""),
                        "card_id": item.get("cardId", "")
                    }
                    cards.append(card)
                except Exception as e:
                    print(f"处理卡片信息失败: {str(e)}")
                    continue
            
            return cards
            
        except Exception as e:
            print(f"获取信用卡列表失败: {str(e)}")
            return []
    
    def get_card_detail(self, card_id: str) -> Dict:
        """获取信用卡详细信息"""
        try:
            print(f"正在访问卡片详情API: {card_id}")
            response = requests.post(
                self.card_detail_url,
                headers=self.headers,
                json={"cardId": card_id},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"API请求失败: {response.status_code}")
                return {}
            
            data = response.json()
            if not data.get("success"):
                print(f"获取数据失败: {data.get('message')}")
                return {}
            
            card_detail = data.get("data", {})
            detail = {
                "name": card_detail.get("cardName", ""),
                "type": card_detail.get("cardType", ""),
                "annual_fee": card_detail.get("annualFee", ""),
                "benefits": self._extract_benefits(card_detail),
                "requirements": self._extract_requirements(card_detail)
            }
            
            return detail
            
        except Exception as e:
            print(f"获取信用卡详情失败: {str(e)}")
            return {}
    
    def _extract_benefits(self, card_detail: Dict) -> Dict:
        """提取权益信息"""
        benefits = {}
        try:
            for benefit in card_detail.get("benefits", []):
                title = benefit.get("title", "")
                description = benefit.get("description", "")
                benefits[title] = description
        except Exception:
            pass
        return benefits
    
    def _extract_requirements(self, card_detail: Dict) -> Dict:
        """提取申请条件"""
        requirements = {}
        try:
            for req in card_detail.get("requirements", []):
                title = req.get("title", "")
                content = req.get("content", "")
                requirements[title] = content
        except Exception:
            pass
        return requirements 