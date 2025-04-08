import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging
from config import DB_CONFIG

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            avatar_url VARCHAR(255),
            full_name VARCHAR(100),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        # 创建会话表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # 创建聊天消息表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id INT NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
        """)

        # 创建用户会话表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # 创建用户银行卡信息表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            bank_name VARCHAR(50) NOT NULL,
            card_number VARCHAR(19) NOT NULL,
            card_type VARCHAR(50) NOT NULL,
            expiry_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # 创建信用卡表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bank VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            level VARCHAR(50),
            annual_fee TEXT,
            benefits JSON,
            requirements JSON,
            points_rule TEXT,
            credit_limit VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY bank_card_name (bank, name)
        )
        """)

        conn.commit()
        logger.info("数据库表创建成功")

    except Error as e:
        logger.error(f"数据库初始化失败: {e}")
        raise e

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_db():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logger.error(f"数据库连接失败: {e}")
        raise e

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