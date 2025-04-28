import mysql.connector

config = {
    'user': 'root',               # 사용자 이름
    'password': 'your_password',  # 비밀번호
    'host': '127.0.0.1',          # 호스트 (로컬이면 그대로)
    'database': 'your_db_name',   # 사용할 DB 이름
    'raise_on_warnings': True
}

try:
    connection = mysql.connector.connect(**config)
    print("✅ MySQL 연결 성공")
    connection.close()
except mysql.connector.Error as err:
    print(f"❌ 연결 실패: {err}")
