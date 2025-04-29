# 📌 main.py

from crawlers.crawler_bss import run_bss_crawling
from crawlers.crawler_sehub import run_sehub_crawling
from crawlers.crawler_seis import run_seis_crawling
from crawlers.crawler_mybiz import run_mybiz_crawling
from openAPI.bizinfo_openAPI import fetch_bizinfo_data

import requests
import os
from dotenv import load_dotenv
import pymysql

# ✅ 환경변수 불러오기
load_dotenv()

# ✅ 디스코드 알림 함수
def send_discord_notification(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ 디스코드 웹훅 URL이 설정되지 않았습니다.")
        return

    payload = {
        "content": message
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("✅ 디스코드 알림 전송 완료")
        else:
            print(f"❌ 디스코드 전송 실패: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ 디스코드 요청 오류: {e}")

# ✅ 중복 제거 함수
def remove_duplicates(data):
    seen = set()
    unique_data = []
    for item in data:
        title_no_space = item['공고 제목'].replace(" ", "")
        title_prefix = title_no_space[:7]
        key = (title_prefix, item['연결 링크'])
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    return unique_data

# ✅ DB에 저장 함수
def save_to_db(data):
    db = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        charset="utf8mb4"
    )
    cursor = db.cursor()

    try:
        # 🔥 테이블 비우기
        cursor.execute("TRUNCATE TABLE support_announcements")
        db.commit()
        print("✅ support_announcements 테이블 초기화 완료")

        # 🔥 데이터 삽입
        insert_query = """
        INSERT INTO support_announcements 
        (title, organization, start_date, end_date, announcement_type, summary, link)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for item in data:
            cursor.execute(insert_query, (
                item.get("공고 제목"),
                item.get("주관기관"),
                item.get("신청 시작일"),
                item.get("신청 종료일"),
                item.get("공고 유형"),
                item.get("상세 내용"),
                item.get("연결 링크")
            ))
        db.commit()
        print("✅ 모든 데이터 저장 완료")

    except Exception as e:
        db.rollback()
        print(f"❌ 데이터 저장 실패: {e}")
        raise e

    finally:
        cursor.close()
        db.close()

# ✅ 메인 함수
def main():
    print("✅ 크롤링 시작!")
    all_results = []

    try:
        all_results.extend(run_bss_crawling())
        all_results.extend(run_sehub_crawling())
        all_results.extend(run_seis_crawling())
        all_results.extend(run_mybiz_crawling())
        all_results.extend(fetch_bizinfo_data())

        print(f"🔵 총 수집된 데이터: {len(all_results)}건")

        final_results = remove_duplicates(all_results)
        print(f"🟢 중복 제거 후 최종 데이터: {len(final_results)}건")

        # 🔥 DB 저장
        save_to_db(final_results)

        # 🔥 디스코드 성공 알림
        send_discord_notification(f"✅ 크롤링 및 DB 저장 완료! ({len(final_results)}건 수집됨)")

    except Exception as e:
        print(f"❌ 전체 프로세스 실패: {e}")
        # 🔥 디스코드 실패 알림
        send_discord_notification(f"❌ 오늘 크롤링 또는 DB 저장 실패!\n{str(e)}")

if __name__ == "__main__":
    main()
