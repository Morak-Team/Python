import mysql.connector
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

config = {
    'user': MYSQL_USER,            
    'password': MYSQL_PASSWORD,
    'host': MYSQL_HOST,       
    'database': MYSQL_DATABASE,
    'raise_on_warnings': True
}

try:
    connection = mysql.connector.connect(**config)
    print("✅ MySQL 연결 성공")

    cursor = connection.cursor()

    # 현재 DB의 모든 테이블 목록 가져오기
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    if tables:
        print("📋 현재 데이터베이스에 있는 테이블 목록:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("⚠️ 데이터베이스에 테이블이 없습니다.")

    cursor.close()
    connection.close()

except mysql.connector.Error as err:
    print(f"❌ 연결 실패: {err}")
