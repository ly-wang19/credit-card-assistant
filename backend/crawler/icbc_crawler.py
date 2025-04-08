"""
工商银行信用卡爬虫
实现工商银行信用卡信息的抓取
"""

from typing import Dict, List
from selenium.webdriver.common.by import By
from .base_crawler import BaseCrawler

class ICBCCrawler(BaseCrawler):
    """工商银行信用卡爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.icbc.com.cn"
        self.card_list_url = f"{self.base_url}/ICBC/信用卡/卡片世界"
    
    def get_card_list(self) -> List[Dict]:
        """获取信用卡列表"""
        try:
            print("正在访问工商银行信用卡列表页面...")
            self.driver.get(self.card_list_url)
            self._random_sleep()
            
            # 等待卡片列表加载
            card_elements = self._find_elements(
                By.CSS_SELECTOR,
                ".card-list .card-item"
            )
            
            cards = []
            for element in card_elements:
                try:
                    # 提取卡片信息
                    card = {
                        "bank": "工商银行",
                        "name": self._find_element(By.CSS_SELECTOR, ".card-name", element).text.strip(),
                        "type": self._find_element(By.CSS_SELECTOR, ".card-type", element).text.strip(),
                        "image": self._find_element(By.CSS_SELECTOR, ".card-image", element).get_attribute("src"),
                        "card_id": self._find_element(By.CSS_SELECTOR, "a", element).get_attribute("href").split("/")[-1].split(".")[0]
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
            detail_url = f"{self.base_url}/ICBC/信用卡/卡片世界/{card_id}.htm"
            print(f"正在访问卡片详情页面: {detail_url}")
            detail_url="https://www.icbc.com.cn/column/1438058474549690490.html"
            
            self.driver.get(detail_url)
            self._random_sleep()
            
            # 等待详情内容加载
            detail_element = self._find_element(By.CSS_SELECTOR, ".card-detail")
            
            if not detail_element:
                print("未找到卡片详情内容")
                return {}
            
            # 提取详细信息
            detail = {
                "name": self._find_element(By.CSS_SELECTOR, ".card-name", detail_element).text.strip(),
                "type": self._find_element(By.CSS_SELECTOR, ".card-type", detail_element).text.strip(),
                "annual_fee": self._find_element(By.CSS_SELECTOR, ".annual-fee", detail_element).text.strip(),
                "benefits": self._extract_benefits(detail_element),
                "requirements": self._extract_requirements(detail_element)
            }
            
            return detail
            
        except Exception as e:
            print(f"获取信用卡详情失败: {str(e)}")
            return {}
    
    def _extract_benefits(self, element) -> Dict:
        """提取权益信息"""
        benefits = {}
        try:
            benefit_elements = self._find_elements(By.CSS_SELECTOR, ".benefit-item", element)
            for benefit in benefit_elements:
                title = self._find_element(By.CSS_SELECTOR, ".benefit-title", benefit).text.strip()
                description = self._find_element(By.CSS_SELECTOR, ".benefit-desc", benefit).text.strip()
                benefits[title] = description
        except Exception:
            pass
        return benefits
    
    def _extract_requirements(self, element) -> Dict:
        """提取申请条件"""
        requirements = {}
        try:
            req_elements = self._find_elements(By.CSS_SELECTOR, ".requirement-item", element)
            for req in req_elements:
                title = self._find_element(By.CSS_SELECTOR, ".req-title", req).text.strip()
                content = self._find_element(By.CSS_SELECTOR, ".req-content", req).text.strip()
                requirements[title] = content
        except Exception:
            pass
        return requirements 