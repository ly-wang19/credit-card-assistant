from ..utils.logger import setup_logger
from ..utils.db import Database
import json

# 设置日志记录器
logger = setup_logger('chat_service')

class ChatService:
    def __init__(self):
        """初始化聊天服务"""
        self.db = Database()
        logger.info("聊天服务初始化完成")

    def process_message(self, message):
        """处理用户消息"""
        try:
            logger.info(f"收到用户消息: {message}")
            
            # 分析消息意图
            intent = self._analyze_intent(message)
            logger.debug(f"分析出的意图: {intent}")
            
            # 根据意图处理消息
            response = self._handle_intent(intent, message)
            logger.info(f"生成回复: {response}")
            
            return response
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
            return "抱歉，我遇到了一些问题，请稍后再试。"

    def _analyze_intent(self, message):
        """分析消息意图"""
        message = message.lower()
        
        # 简单的关键词匹配
        if any(kw in message for kw in ['推荐', '建议', '哪个好']):
            return 'recommend'
        elif any(kw in message for kw in ['查询', '搜索', '找']):
            return 'search'
        elif any(kw in message for kw in ['比较', '区别']):
            return 'compare'
        elif any(kw in message for kw in ['年费', '费用']):
            return 'fee'
        elif any(kw in message for kw in ['权益', '优惠', '好处']):
            return 'benefits'
        else:
            return 'general'

    def _handle_intent(self, intent, message):
        """根据意图处理消息"""
        try:
            if intent == 'recommend':
                return self._handle_recommendation(message)
            elif intent == 'search':
                return self._handle_search(message)
            elif intent == 'compare':
                return self._handle_comparison(message)
            elif intent == 'fee':
                return self._handle_fee_query(message)
            elif intent == 'benefits':
                return self._handle_benefits_query(message)
            else:
                return self._handle_general_query(message)
        except Exception as e:
            logger.error(f"处理意图 {intent} 时出错: {str(e)}")
            return "抱歉，我暂时无法处理这个问题。请换个方式提问或稍后再试。"

    def _handle_recommendation(self, message):
        """处理推荐请求"""
        try:
            # 获取所有信用卡
            sql = """
            SELECT bank_name, card_name, card_level, annual_fee, 
                   credit_limit, benefits
            FROM credit_cards
            LIMIT 3
            """
            self.db.execute(sql)
            cards = self.db.fetchall()
            
            # 构建推荐回复
            response = "根据您的需求，我为您推荐以下信用卡：\n\n"
            for card in cards:
                response += f"【{card['bank_name']} {card['card_name']}】\n"
                response += f"等级：{card['card_level']}\n"
                response += f"年费：{card['annual_fee']}\n"
                response += f"额度：{card['credit_limit']}\n"
                
                # 解析权益信息
                try:
                    benefits = json.loads(card['benefits'])
                    response += "主要权益：\n"
                    for key, value in benefits.items():
                        response += f"- {value}\n"
                except:
                    response += f"主要权益：{card['benefits']}\n"
                
                response += "\n"
            
            return response
        except Exception as e:
            logger.error(f"处理推荐请求时出错: {str(e)}")
            return "抱歉，生成推荐时出现错误。请稍后再试。"

    def _handle_search(self, message):
        """处理搜索请求"""
        try:
            # 提取搜索关键词
            keywords = message.replace('查询', '').replace('搜索', '').replace('找', '').strip()
            
            # 搜索数据库
            sql = """
            SELECT bank_name, card_name, card_level, annual_fee
            FROM credit_cards
            WHERE bank_name LIKE %s 
               OR card_name LIKE %s
               OR card_level LIKE %s
            LIMIT 5
            """
            search_param = f"%{keywords}%"
            self.db.execute(sql, (search_param, search_param, search_param))
            results = self.db.fetchall()
            
            if not results:
                return f'抱歉，没有找到与"{keywords}"相关的信用卡。'
            
            response = f"为您找到以下相关信用卡：\n\n"
            for card in results:
                response += f"【{card['bank_name']} {card['card_name']}】\n"
                response += f"等级：{card['card_level']}\n"
                response += f"年费：{card['annual_fee']}\n\n"
            
            return response
        except Exception as e:
            logger.error(f"处理搜索请求时出错: {str(e)}")
            return "抱歉，搜索时出现错误。请稍后再试。"

    def _handle_comparison(self, message):
        """处理比较请求"""
        try:
            response = "您想比较的信用卡信息如下：\n\n"
            response += "抱歉，比较功能正在开发中。请先尝试分别查询各个信用卡的信息。"
            return response
        except Exception as e:
            logger.error(f"处理比较请求时出错: {str(e)}")
            return "抱歉，比较功能暂时无法使用。"

    def _handle_fee_query(self, message):
        """处理年费查询"""
        try:
            # 提取银行或卡片名称
            keywords = message.replace('年费', '').replace('费用', '').strip()
            
            sql = """
            SELECT bank_name, card_name, annual_fee
            FROM credit_cards
            WHERE bank_name LIKE %s 
               OR card_name LIKE %s
            LIMIT 5
            """
            search_param = f"%{keywords}%"
            self.db.execute(sql, (search_param, search_param))
            results = self.db.fetchall()
            
            if not results:
                return f'抱歉，没有找到与"{keywords}"相关的年费信息。'
            
            response = f"为您找到以下年费信息：\n\n"
            for card in results:
                response += f"【{card['bank_name']} {card['card_name']}】\n"
                response += f"年费政策：{card['annual_fee']}\n\n"
            
            return response
        except Exception as e:
            logger.error(f"处理年费查询时出错: {str(e)}")
            return "抱歉，查询年费信息时出现错误。请稍后再试。"

    def _handle_benefits_query(self, message):
        """处理权益查询"""
        try:
            # 提取银行或卡片名称
            keywords = message.replace('权益', '').replace('优惠', '').replace('好处', '').strip()
            
            sql = """
            SELECT bank_name, card_name, benefits
            FROM credit_cards
            WHERE bank_name LIKE %s 
               OR card_name LIKE %s
            LIMIT 3
            """
            search_param = f"%{keywords}%"
            self.db.execute(sql, (search_param, search_param))
            results = self.db.fetchall()
            
            if not results:
                return f'抱歉，没有找到与"{keywords}"相关的权益信息。'
            
            response = f"为您找到以下权益信息：\n\n"
            for card in results:
                response += f"【{card['bank_name']} {card['card_name']}】\n"
                try:
                    benefits = json.loads(card['benefits'])
                    for key, value in benefits.items():
                        response += f"- {value}\n"
                except:
                    response += f"{card['benefits']}\n"
                response += "\n"
            
            return response
        except Exception as e:
            logger.error(f"处理权益查询时出错: {str(e)}")
            return "抱歉，查询权益信息时出现错误。请稍后再试。"

    def _handle_general_query(self, message):
        """处理一般性查询"""
        return "您可以问我关于信用卡的问题，比如：\n\n" + \
               "1. 推荐一些适合我的信用卡\n" + \
               "2. 查询某个银行的信用卡\n" + \
               "3. 比较不同信用卡的区别\n" + \
               "4. 查询信用卡年费政策\n" + \
               "5. 了解信用卡的权益" 