"""
基础爬虫类
定义所有银行爬虫的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import random
import logging
import os
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类，定义通用接口"""
    
    def __init__(self, bank_name: str, base_url: str):
        """初始化爬虫"""
        self.bank_name = bank_name
        self.base_url = base_url
        self.setup_driver()
        
    def setup_driver(self):
        """设置Selenium驱动"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # 添加更多选项以提高稳定性
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        
        retry_count = 3
        while retry_count > 0:
            try:
                self.driver = webdriver.Chrome(options=options)
                self.wait = WebDriverWait(self.driver, 15)  # 增加等待时间
                break
            except Exception as e:
                retry_count -= 1
                if retry_count == 0:
                    raise e
                logger.warning(f"创建驱动失败，剩余重试次数：{retry_count}")
                time.sleep(2)
    
    @abstractmethod
    def get_card_list(self) -> List[Dict]:
        """获取信用卡列表"""
        pass
    
    @abstractmethod
    def get_card_detail(self, card_id: str) -> Dict:
        """获取信用卡详细信息"""
        pass
    
    def crawl_all_cards(self, save_dir: str = "results") -> List[Dict]:
        """抓取所有信用卡信息"""
        try:
            logger.info(f"\n开始抓取{self.bank_name}信用卡信息...")
            
            # 获取信用卡列表
            cards = self.get_card_list()
            if not cards:
                logger.warning(f"未获取到{self.bank_name}的信用卡列表")
                return []
            
            logger.info(f"获取到 {len(cards)} 张信用卡")
            
            # 获取每张卡的详细信息
            for card in cards:
                try:
                    card_id = card.get("card_id")
                    if not card_id:
                        continue
                    
                    logger.info(f"正在获取卡片详情: {card.get('name', '未知卡片')}")
                    detail = self.get_card_detail(card_id)
                    if detail:
                        card.update(detail)
                    
                except Exception as e:
                    logger.error(f"获取卡片详情失败: {str(e)}")
                    continue
                
                finally:
                    self._random_sleep(1, 3)
            
            # 保存结果
            self.save_results(cards, save_dir)
            
            return cards
            
        except Exception as e:
            logger.error(f"抓取信用卡信息失败: {str(e)}")
            return []
    
    def save_results(self, cards: List[Dict], save_dir: str = "results"):
        """保存抓取结果"""
        try:
            # 确保结果目录存在
            bank_dir = os.path.join(save_dir, self.bank_name)
            if not os.path.exists(bank_dir):
                os.makedirs(bank_dir)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON格式
            json_file = os.path.join(bank_dir, f"credit_cards_{timestamp}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)
            
            # 保存文本格式
            txt_file = os.path.join(bank_dir, f"credit_cards_{timestamp}.txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                for card in cards:
                    f.write(f"卡片名称: {card.get('name', '未知')}\n")
                    f.write(f"卡片类型: {card.get('type', '未知')}\n")
                    f.write(f"年费: {card.get('annual_fee', '未知')}\n")
                    
                    # 写入权益信息
                    f.write("\n权益信息:\n")
                    for title, desc in card.get("benefits", {}).items():
                        f.write(f"  {title}: {desc}\n")
                    
                    # 写入申请条件
                    f.write("\n申请条件:\n")
                    for title, content in card.get("requirements", {}).items():
                        f.write(f"  {title}: {content}\n")
                    
                    f.write("\n" + "="*50 + "\n\n")
            
            logger.info(f"结果已保存到: {bank_dir}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")
    
    def _find_element(self, by: By, value: str, parent: Optional[webdriver.remote.webelement.WebElement] = None, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """查找元素，支持超时和父元素"""
        try:
            if parent:
                element = WebDriverWait(self.driver, timeout).until(
                    lambda d: parent.find_element(by, value)
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            return element if element.is_displayed() else None
        except (TimeoutException, NoSuchElementException):
            return None
    
    def _find_elements(self, by: By, value: str, parent: Optional[webdriver.remote.webelement.WebElement] = None, timeout: int = 10) -> List[webdriver.remote.webelement.WebElement]:
        """查找多个元素，支持超时和父元素"""
        try:
            if parent:
                elements = WebDriverWait(self.driver, timeout).until(
                    lambda d: parent.find_elements(by, value)
                )
            else:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((by, value))
                )
            return [e for e in elements if e.is_displayed()]
        except (TimeoutException, NoSuchElementException):
            return []
    
    def _scroll_to_element(self, element: webdriver.remote.webelement.WebElement):
        """滚动到指定元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self._random_sleep(0.5, 1)
        except:
            pass
    
    def _random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机休眠，避免请求过于频繁"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _safe_get_text(self, element: Optional[webdriver.remote.webelement.WebElement]) -> str:
        """安全地获取元素文本"""
        try:
            return element.text.strip() if element else ""
        except:
            return ""
    
    def _safe_get_attribute(self, element: Optional[webdriver.remote.webelement.WebElement], attribute: str) -> str:
        """安全地获取元素属性"""
        try:
            return element.get_attribute(attribute).strip() if element else ""
        except:
            return ""
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass 