import sys
import os
from pathlib import Path
import bcrypt
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.database.db import get_db_connection

def create_test_user():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 测试用户数据
        test_user = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': '123456',  # 简单密码仅用于测试
            'full_name': '测试用户',
            'phone': '13800138000'
        }

        # 生成密码哈希
        password_bytes = test_user['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)

        # 准备插入语句
        insert_query = """
        INSERT INTO users 
        (username, email, password_hash, full_name, phone)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        password_hash = VALUES(password_hash),
        full_name = VALUES(full_name),
        phone = VALUES(phone),
        updated_at = CURRENT_TIMESTAMP
        """

        values = (
            test_user['username'],
            test_user['email'],
            password_hash.decode('utf-8'),
            test_user['full_name'],
            test_user['phone']
        )

        cursor.execute(insert_query, values)
        conn.commit()

        print(f"测试用户创建成功！")
        print(f"用户名: {test_user['username']}")
        print(f"密码: {test_user['password']}")
        print(f"邮箱: {test_user['email']}")

    except Exception as e:
        print(f"创建测试用户时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    create_test_user() 