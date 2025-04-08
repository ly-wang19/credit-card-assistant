import mysql.connector
from dotenv import load_dotenv
import os
from .logger import setup_logger

# 设置日志记录器
logger = setup_logger('database')

# 加载环境变量
load_dotenv()

class Database:
    def __init__(self):
        """初始化数据库连接配置"""
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '1996129.yin',
            'database': 'credit_card_assistant'
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    def disconnect(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {str(e)}")

    def execute(self, sql, params=None):
        """执行SQL语句"""
        try:
            if not self.conn or not self.conn.is_connected():
                self.connect()
            self.cursor.execute(sql, params or ())
            logger.debug(f"执行SQL: {sql}")
            return self.cursor
        except Exception as e:
            logger.error(f"执行SQL出错: {str(e)}")
            raise

    def fetchall(self):
        """获取所有结果"""
        return self.cursor.fetchall()

    def fetchone(self):
        """获取单个结果"""
        return self.cursor.fetchone()

    def commit(self):
        """提交事务"""
        try:
            self.conn.commit()
            logger.debug("事务已提交")
        except Exception as e:
            logger.error(f"提交事务时出错: {str(e)}")
            raise

    def rollback(self):
        """回滚事务"""
        try:
            self.conn.rollback()
            logger.debug("事务已回滚")
        except Exception as e:
            logger.error(f"回滚事务时出错: {str(e)}")
            raise 