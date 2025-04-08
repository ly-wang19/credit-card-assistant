"""
信用卡详细信息爬虫
使用搜索引擎API获取信用卡名称和链接，然后使用DeepSeek分析内容
"""

import os
import json
import logging
import requests
import time
import random
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CardDetailCrawler:
    """信用卡详细信息爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        # 加载环境变量
        load_dotenv()
        
        # 初始化API密钥
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not self.deepseek_api_key or not self.serper_api_key:
            raise ValueError("请确保在.env文件中设置了DEEPSEEK_API_KEY和SERPER_API_KEY")
        
        # API端点
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.serper_api_url = "https://google.serper.dev/search"
        
        logger.info("正在初始化Selenium驱动...")
        self.setup_driver()
        
        logger.info("正在读取银行列表...")
        self.banks = self._read_bank_list()
        logger.info(f"成功读取 {len(self.banks)} 个银行")
    
    def setup_driver(self):
        """设置Selenium驱动"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-notifications')
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Selenium驱动初始化成功")
        except Exception as e:
            logger.error(f"Selenium驱动初始化失败: {str(e)}")
            raise
    
    def _read_bank_list(self) -> List[str]:
        """读取银行列表"""
        return [
            "中国农业银行",
            "中国银行",
            "中国建设银行",
            "交通银行",
            "招商银行",
            "浦发银行",
            "中信银行",
            "中国民生银行",
            "兴业银行",
            "平安银行",
            "广发银行",
            "华夏银行"
        ]
    
    def _search_credit_cards(self, bank_name: str) -> List[str]:
        """搜索银行的信用卡"""
        try:
            logger.info(f"正在搜索 {bank_name} 的信用卡...")
            
            # 构建搜索查询
            query = f"{bank_name}信用卡 site:.cn"
            
            # 调用Serper API
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "gl": "cn",
                "hl": "zh-cn",
                "num": 10
            }
            
            response = requests.post(
                self.serper_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Serper API请求失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return []
            
            results = response.json()
            
            # 提取信用卡名称
            prompt = f"""
            请从以下搜索结果中提取所有信用卡的名称：
            
            {json.dumps(results, ensure_ascii=False)}
            
            请以JSON数组格式返回信用卡名称列表，格式如下：
            ["信用卡1", "信用卡2", "信用卡3"]
            
            注意：
            1. 只返回完整的信用卡名称
            2. 不要包含重复的名称
            3. 确保是真实的信用卡产品
            4. 直接返回JSON数组，不要包含其他文本
            """
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(
                self.deepseek_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API请求失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return []
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 清理JSON内容
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                card_names = json.loads(content)
                logger.info(f"找到 {len(card_names)} 张信用卡")
                return card_names
            except json.JSONDecodeError as e:
                logger.error(f"无法解析信用卡名称JSON: {str(e)}")
                logger.error(f"清理后的内容: {content}")
                return []
            
        except Exception as e:
            logger.error(f"搜索信用卡失败: {str(e)}")
            return []
    
    def _search_card_detail(self, bank_name: str, card_name: str) -> Optional[Dict]:
        """搜索信用卡详细信息"""
        try:
            logger.info(f"正在搜索 {card_name} 的详细信息...")
            
            # 构建搜索查询
            query = f"{bank_name} {card_name} 信用卡 申请条件 权益"
            
            # 调用Serper API
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "gl": "cn",
                "hl": "zh-cn",
                "num": 5
            }
            
            response = requests.post(
                self.serper_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Serper API请求失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return None
            
            results = response.json()
            
            # 提取信用卡详细信息
            prompt = f"""
            请从以下搜索结果中提取信用卡的详细信息：
            
            银行：{bank_name}
            信用卡：{card_name}
            搜索结果：{json.dumps(results, ensure_ascii=False)}
            
            请提取以下信息并以JSON格式返回：
            1. 卡片等级（白金卡/金卡/普卡等）
            2. 年费政策
            3. 主要权益（至少3个）
            4. 申请条件
            5. 积分规则
            6. 额度范围
            
            格式如下：
            {{
                "level": "卡片等级",
                "annual_fee": "年费政策",
                "benefits": {{
                    "权益1": "描述",
                    "权益2": "描述",
                    "权益3": "描述"
                }},
                "requirements": {{
                    "条件1": "描述",
                    "条件2": "描述"
                }},
                "points_rule": "积分规则",
                "credit_limit": "额度范围"
            }}
            
            注意：直接返回JSON，不要包含其他文本。
            """
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(
                self.deepseek_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API请求失败: {response.status_code}")
                logger.error(f"错误信息: {response.text}")
                return None
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 清理JSON内容
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                card_info = json.loads(content)
                logger.info("成功提取信用卡详细信息")
                return card_info
            except json.JSONDecodeError as e:
                logger.error(f"无法解析信用卡详细信息JSON: {str(e)}")
                logger.error(f"清理后的内容: {content}")
                return None
            
        except Exception as e:
            logger.error(f"搜索信用卡详细信息失败: {str(e)}")
            return None
    
    def crawl_all_cards(self):
        """爬取所有银行的信用卡信息"""
        try:
            all_results = []
            total_banks = len(self.banks)
            
            for index, bank in enumerate(self.banks, 1):
                try:
                    logger.info(f"\n[{index}/{total_banks}] 开始处理 {bank}...")
                    
                    # 搜索该银行的信用卡
                    card_names = self._search_credit_cards(bank)
                    
                    if not card_names:
                        logger.warning(f"未找到 {bank} 的信用卡")
                        continue
                    
                    # 获取每张卡的详细信息
                    for card_name in card_names:
                        try:
                            card_info = self._search_card_detail(bank, card_name)
                            
                            if card_info:
                                result = {
                                    "bank": bank,
                                    "name": card_name,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                result.update(card_info)
                                all_results.append(result)
                                logger.info(f"成功获取 {card_name} 的详细信息")
                            
                            # 随机延迟
                            time.sleep(random.uniform(2, 4))
                            
                        except Exception as e:
                            logger.error(f"处理 {card_name} 时出错: {str(e)}")
                            continue
                    
                except Exception as e:
                    logger.error(f"处理 {bank} 时出错: {str(e)}")
                    continue
            
            # 保存结果
            if all_results:
                self.save_results(all_results)
                logger.info(f"\n成功保存 {len(all_results)} 条信用卡信息")
            else:
                logger.warning("未获取到任何信用卡信息")
            
        except Exception as e:
            logger.error(f"爬取过程中出现错误: {str(e)}")
        finally:
            try:
                self.driver.quit()
                logger.info("Selenium驱动已关闭")
            except:
                pass
    
    def save_results(self, results: List[Dict], save_dir: str = "results"):
        """保存结果到文件"""
        try:
            # 确保结果目录存在
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                logger.info(f"创建结果目录: {save_dir}")
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON格式
            json_file = os.path.join(save_dir, f"credit_cards_detail_{timestamp}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON结果已保存到: {json_file}")
            
            # 保存文本格式
            txt_file = os.path.join(save_dir, f"credit_cards_detail_{timestamp}.txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                for result in results:
                    f.write(f"银行: {result['bank']}\n")
                    f.write(f"信用卡名称: {result['name']}\n")
                    f.write(f"卡片等级: {result.get('level', '未知')}\n")
                    f.write(f"年费政策: {result.get('annual_fee', '未知')}\n")
                    f.write(f"额度范围: {result.get('credit_limit', '未知')}\n")
                    f.write(f"积分规则: {result.get('points_rule', '未知')}\n")
                    
                    f.write("\n权益信息:\n")
                    for title, desc in result.get('benefits', {}).items():
                        f.write(f"  {title}: {desc}\n")
                    
                    f.write("\n申请条件:\n")
                    for title, desc in result.get('requirements', {}).items():
                        f.write(f"  {title}: {desc}\n")
                    
                    f.write("\n" + "="*50 + "\n\n")
            logger.info(f"文本结果已保存到: {txt_file}")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}") 