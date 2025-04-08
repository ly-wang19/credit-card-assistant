"""
银行信用卡爬虫
用于定位各大银行的信用卡页面
"""

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

class BankCreditCardLocator:
    """银行信用卡页面定位器"""
    
    def __init__(self):
        """初始化Selenium"""
        self.setup_driver()
        
        # 银行主页和信用卡关键词映射
        self.banks = {
            "中国工商银行": {
                "url": "https://www.icbc.com.cn/",
                "keywords": ["信用卡", "卡片", "信用卡中心"],
                "special_urls": [
                    "https://cards.icbc.com.cn/",
                    "https://www.icbc.com.cn/ICBC/金融信息/信用卡/"
                ]
            },
            "中国农业银行": {
                "url": "https://www.abchina.com/",
                "keywords": ["信用卡", "卡片中心", "信用卡中心"],
                "special_urls": [
                    "https://www.abchina.com/cn/CreditCard/",
                    "https://creditcard.abchina.com/"
                ]
            },
            "中国银行": {
                "url": "https://www.boc.cn/",
                "keywords": ["信用卡", "卡片业务", "信用卡中心"],
                "special_urls": [
                    "https://www.boc.cn/bcservice/bc1/",
                    "https://www.boc.cn/creditcard/"
                ]
            },
            "中国建设银行": {
                "url": "https://www.ccb.com/",
                "keywords": ["信用卡", "龙卡", "信用卡中心"],
                "special_urls": [
                    "http://credit.ccb.com/",
                    "https://creditcard.ccb.com/"
                ]
            },
            "交通银行": {
                "url": "https://www.bankcomm.com/",
                "keywords": ["信用卡", "沃德卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.bankcomm.com/",
                    "https://www.bankcomm.com/creditcard/"
                ]
            },
            "招商银行": {
                "url": "https://www.cmbchina.com/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "http://cc.cmbchina.com/",
                    "https://creditcard.cmbchina.com/"
                ]
            },
            "浦发银行": {
                "url": "https://www.spdb.com.cn/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.spdb.com.cn/",
                    "https://www.spdb.com.cn/creditcard/"
                ]
            },
            "中信银行": {
                "url": "https://www.citicbank.com/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.ecitic.com/",
                    "https://card.ecitic.com/"
                ]
            },
            "中国民生银行": {
                "url": "https://www.cmbc.com.cn/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.cmbc.com.cn/",
                    "https://www.cmbc.com.cn/cs/creditcard/"
                ]
            },
            "兴业银行": {
                "url": "https://www.cib.com.cn/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.cib.com.cn/",
                    "https://www.cib.com.cn/creditcard/"
                ]
            },
            "平安银行": {
                "url": "https://bank.pingan.com/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.pingan.com/",
                    "https://bank.pingan.com/creditcard/"
                ]
            },
            "广发银行": {
                "url": "https://www.cgbchina.com.cn/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "http://card.cgbchina.com.cn/",
                    "https://www.cgbchina.com.cn/creditcard/"
                ]
            },
            "华夏银行": {
                "url": "https://www.hxb.com.cn/",
                "keywords": ["信用卡", "信用卡中心"],
                "special_urls": [
                    "https://creditcard.hxb.com.cn/",
                    "https://www.hxb.com.cn/grjr/xyk/"
                ]
            }
        }
    
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
    
    def locate_credit_card_pages(self):
        """定位各银行信用卡页面"""
        results = {}
        
        # 创建结果目录
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        for bank_name, bank_info in self.banks.items():
            retry_count = 3  # 每个银行最多重试3次
            while retry_count > 0:
                try:
                    logger.info(f"\n正在访问{bank_name}...")
                    
                    # 首先尝试特殊URL
                    for special_url in bank_info.get("special_urls", []):
                        try:
                            self.driver.get(special_url)
                            self._random_sleep(1, 3)
                            
                            # 验证页面是否正确加载
                            if self._verify_page_load():
                                results[bank_name] = {
                                    "url": special_url,
                                    "source": "special_url",
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                logger.info(f"✅ {bank_name}信用卡页面: {special_url} (特殊URL)")
                                break
                        except Exception as e:
                            logger.debug(f"访问特殊URL {special_url} 失败: {str(e)}")
                            continue
                    
                    # 如果特殊URL都失败了，尝试从主页查找
                    if bank_name not in results:
                        self.driver.get(bank_info["url"])
                        self._random_sleep(1, 3)
                        
                        # 尝试查找信用卡链接
                        credit_card_link = self._find_credit_card_link(bank_info["keywords"])
                        
                        if credit_card_link:
                            href = credit_card_link.get_attribute("href")
                            if href:
                                # 处理相对URL
                                if not href.startswith(("http://", "https://")):
                                    base_url = bank_info["url"].rstrip("/")
                                    href = f"{base_url}/{href.lstrip('/')}"
                                results[bank_name] = {
                                    "url": href,
                                    "source": "main_page",
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                logger.info(f"✅ {bank_name}信用卡页面: {href}")
                            else:
                                logger.warning(f"❌ {bank_name}：未找到有效的信用卡链接")
                        else:
                            logger.warning(f"❌ {bank_name}：未找到信用卡链接")
                    
                    # 如果成功找到链接，跳出重试循环
                    if bank_name in results:
                        break
                    
                except WebDriverException as e:
                    retry_count -= 1
                    if retry_count > 0:
                        logger.warning(f"访问{bank_name}失败，将重试。错误：{str(e)}")
                        self._random_sleep(5, 10)  # 失败后等待更长时间
                        continue
                    else:
                        logger.error(f"❌ {bank_name}访问失败：{str(e)}")
                except Exception as e:
                    logger.error(f"❌ {bank_name}出现未知错误：{str(e)}")
                    break
                
                finally:
                    self._random_sleep(1, 3)
                    retry_count -= 1
        
        return results
    
    def _find_credit_card_link(self, keywords):
        """查找信用卡链接"""
        for keyword in keywords:
            try:
                # 使用多种选择器尝试定位
                selectors = [
                    f"//a[contains(text(), '{keyword}')]",  # XPath文本匹配
                    f"//a[contains(@title, '{keyword}')]",  # XPath标题匹配
                    f"//div[contains(text(), '{keyword}')]//ancestor::a",  # XPath祖先元素
                    f"//span[contains(text(), '{keyword}')]//ancestor::a",  # XPath span文本
                    f"//img[contains(@alt, '{keyword}')]//ancestor::a",  # XPath 图片alt文本
                    f"//a[contains(@href, '{keyword}')]",  # XPath href匹配
                    f"a:contains('{keyword}')"  # CSS文本包含
                ]
                
                for selector in selectors:
                    try:
                        if selector.startswith("//"):
                            element = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                        else:
                            element = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                        if element and element.is_displayed():
                            return element
                    except:
                        continue
                        
            except (TimeoutException, NoSuchElementException):
                continue
        
        return None
    
    def _verify_page_load(self):
        """验证页面是否正确加载"""
        try:
            # 等待body元素加载完成
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 检查页面标题是否包含关键词
            title = self.driver.title.lower()
            keywords = ["信用卡", "信用卡中心", "信用卡官网", "卡片", "信用卡产品"]
            if any(keyword in title for keyword in keywords):
                return True
            
            # 检查页面内容是否包含关键词
            content = self.driver.page_source.lower()
            return any(keyword in content for keyword in keywords)
            
        except:
            return False
    
    def _random_sleep(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """随机休眠，避免请求过于频繁"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass

def save_results(results, results_dir="results"):
    """保存结果到文件"""
    # 确保结果目录存在
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON格式
    json_file = os.path.join(results_dir, f"bank_credit_card_pages_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存文本格式
    txt_file = os.path.join(results_dir, f"bank_credit_card_pages_{timestamp}.txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        for bank, info in results.items():
            f.write(f"{bank}:\n")
            f.write(f"  URL: {info['url']}\n")
            f.write(f"  来源: {info['source']}\n")
            f.write(f"  时间: {info['timestamp']}\n")
            f.write("\n")
    
    return json_file, txt_file

def main():
    """主函数"""
    try:
        logger.info("开始定位银行信用卡页面...")
        
        locator = BankCreditCardLocator()
        credit_card_pages = locator.locate_credit_card_pages()
        
        # 保存结果
        json_file, txt_file = save_results(credit_card_pages)
        
        logger.info(f"\n信用卡页面定位完成！")
        logger.info(f"JSON结果已保存到：{json_file}")
        logger.info(f"文本结果已保存到：{txt_file}")
        
    except Exception as e:
        logger.error(f"程序运行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main()

    