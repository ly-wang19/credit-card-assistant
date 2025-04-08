from ..utils.db import Database
from ..utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger('credit_card_service')

class CreditCardService:
    def __init__(self):
        """初始化信用卡服务"""
        self.db = Database()
        logger.info("信用卡服务初始化完成")

    def get_all_cards(self):
        """获取所有信用卡信息"""
        try:
            sql = """
            SELECT id, bank_name, card_name, card_level, annual_fee, 
                   credit_limit, points_rule, benefits, requirements 
            FROM credit_cards
            """
            self.db.execute(sql)
            cards = self.db.fetchall()
            logger.info(f"成功获取 {len(cards)} 张信用卡信息")
            return cards
        except Exception as e:
            logger.error(f"获取信用卡信息失败: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def get_card_by_id(self, card_id):
        """根据ID获取信用卡信息"""
        try:
            sql = """
            SELECT id, bank_name, card_name, card_level, annual_fee,
                   credit_limit, points_rule, benefits, requirements
            FROM credit_cards
            WHERE id = %s
            """
            self.db.execute(sql, (card_id,))
            card = self.db.fetchone()
            if card:
                logger.info(f"成功获取ID为 {card_id} 的信用卡信息")
            else:
                logger.warning(f"未找到ID为 {card_id} 的信用卡信息")
            return card
        except Exception as e:
            logger.error(f"获取信用卡信息失败: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def search_cards(self, keyword):
        """搜索信用卡"""
        try:
            sql = """
            SELECT id, bank_name, card_name, card_level, annual_fee,
                   credit_limit, points_rule, benefits, requirements
            FROM credit_cards
            WHERE bank_name LIKE %s 
               OR card_name LIKE %s
               OR card_level LIKE %s
            """
            search_param = f"%{keyword}%"
            self.db.execute(sql, (search_param, search_param, search_param))
            cards = self.db.fetchall()
            logger.info(f"使用关键词 '{keyword}' 搜索到 {len(cards)} 张信用卡")
            return cards
        except Exception as e:
            logger.error(f"搜索信用卡失败: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def get_cards_by_bank(self, bank_name):
        """获取指定银行的信用卡"""
        try:
            sql = """
            SELECT id, bank_name, card_name, card_level, annual_fee,
                   credit_limit, points_rule, benefits, requirements
            FROM credit_cards
            WHERE bank_name = %s
            """
            self.db.execute(sql, (bank_name,))
            cards = self.db.fetchall()
            logger.info(f"成功获取 {bank_name} 的 {len(cards)} 张信用卡信息")
            return cards
        except Exception as e:
            logger.error(f"获取银行信用卡信息失败: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def get_cards_by_level(self, card_level):
        """获取指定等级的信用卡"""
        try:
            sql = """
            SELECT id, bank_name, card_name, card_level, annual_fee,
                   credit_limit, points_rule, benefits, requirements
            FROM credit_cards
            WHERE card_level LIKE %s
            """
            self.db.execute(sql, (f"%{card_level}%",))
            cards = self.db.fetchall()
            logger.info(f"成功获取 {card_level} 等级的 {len(cards)} 张信用卡信息")
            return cards
        except Exception as e:
            logger.error(f"获取等级信用卡信息失败: {str(e)}")
            raise
        finally:
            self.db.disconnect() 