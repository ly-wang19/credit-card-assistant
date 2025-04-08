import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USERNAME', 'root'),
            password=os.getenv('DB_PASSWORD', '1996129.yin'),
            database=os.getenv('DB_DATABASE', 'credit_card_assistant')
        )
        logger.info("数据库连接成功")
        return connection
    except Error as e:
        logger.error(f"数据库连接失败: {e}")
        raise