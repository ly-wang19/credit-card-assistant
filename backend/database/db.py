import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        # 获取环境变量
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USERNAME', 'root')
        password = os.getenv('DB_PASSWORD', '1996129.yin')
        database = os.getenv('DB_DATABASE', 'credit_card_assistant')
        
        logger.debug(f"尝试连接数据库: host={host}, port={port}, user={user}, database={database}")
        
        # 创建连接配置
        config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'use_unicode': True,
            'get_warnings': True,
            'raise_on_warnings': True,
            'connection_timeout': 10
        }
        
        logger.debug(f"数据库连接配置: {config}")
        
        connection = mysql.connector.connect(**config)
        
        # 设置连接选项
        connection.autocommit = True
        
        # 测试连接
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # 测试查询credit_cards表
        try:
            cursor.execute("SELECT COUNT(*) as count FROM credit_cards")
            count_result = cursor.fetchone()
            logger.debug(f"credit_cards表中的记录数: {count_result['count'] if count_result else 0}")
            
            cursor.execute("SHOW COLUMNS FROM credit_cards")
            columns = cursor.fetchall()
            logger.debug(f"credit_cards表的列结构: {columns}")
            
            cursor.execute("SELECT * FROM credit_cards LIMIT 1")
            sample_record = cursor.fetchone()
            logger.debug(f"credit_cards表的示例记录: {sample_record}")
        except Error as e:
            logger.error(f"测试credit_cards表时出错: {e}")
        finally:
            cursor.close()
        
        if result and result.get('1') == 1:
            logger.info("数据库连接测试成功")
        else:
            logger.warning("数据库连接测试未返回预期结果")
        
        return connection
    except Error as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    except Exception as e:
        logger.error(f"创建数据库连接时发生未知错误: {e}")
        raise