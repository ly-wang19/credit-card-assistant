import mysql.connector
import bcrypt

# 数据库连接
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1996129.yin',
    database='credit_card_db'
)

cursor = db.cursor()

# 生成密码哈希
password = '123456'
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# 插入用户
cursor.execute('DELETE FROM users WHERE email=%s', ('test@example.com',))
cursor.execute(
    'INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)',
    ('test', 'test@example.com', hashed.decode(), '测试用户')
)

db.commit()
cursor.close()
db.close()

print('用户创建成功') 