# 📌 main.py
# 📌 main.py

from crawlers.crawler_bss import run_bss_crawling
from crawlers.crawler_sehub import run_sehub_crawling
from crawlers.crawler_seis import run_seis_crawling
from crawlers.crawler_mybiz import run_mybiz_crawling
from openAPI.bizinfo_openAPI import fetch_bizinfo_data  # 🔥 추가! (API 불러오기)

def remove_duplicates(data):
    seen = set()
    unique_data = []
    for item in data:
        # 🔥 공백 제거한 제목 앞 7글자 추출
        title_no_space = item['공고 제목'].replace(" ", "")  # 공백 제거
        title_prefix = title_no_space[:7]  # 앞 7글자 자르기
        key = (title_prefix, item['연결 링크'])
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    return unique_data


def main():
    print("✅ 크롤링 시작!")

    all_results = []

    # 각 사이트 크롤링 실행
    all_results.extend(run_bss_crawling())
    all_results.extend(run_sehub_crawling())
    all_results.extend(run_seis_crawling())
    all_results.extend(run_mybiz_crawling())
    all_results.extend(fetch_bizinfo_data())  # 🔥 API도 함께 실행해서 결과 합치기

    print(f"🔵 총 수집된 데이터: {len(all_results)}건")

    # 중복 제거
    final_results = remove_duplicates(all_results)

    print(f"🟢 중복 제거 후 최종 데이터: {len(final_results)}건")

    # 최종 출력
    for idx, item in enumerate(final_results, 1):
        print(f"[{idx}] {item}")

if __name__ == "__main__":
    main()
