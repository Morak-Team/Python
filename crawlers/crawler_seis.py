# 📌 사회적 기업 포털 크롤러
# GPT로 상세내용 다듬기 필요

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

EXCLUDED_KEYS = {
    "수행기관 구분", "담당부서", "담당자 및 연락처", "지원지역", "첨부파일", ""
}

def parse_period(period_text):
    """ '2025-04-22 ~ 2025-05-09' 형태를 start, end로 나누는 함수 """
    if not period_text:
        return "미정", "미정"
    match = re.match(r"(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})", period_text)
    if match:
        return match.group(1), match.group(2)
    else:
        return "미정", "미정"

def parse_detail_page(driver):
    result = {}
    details = driver.find_elements(By.CSS_SELECTOR, ".view_box_items li")
    for li in details:
        try:
            dt = li.find_element(By.CSS_SELECTOR, "dt").text.strip().replace(":", "")
            dd = li.find_element(By.CSS_SELECTOR, "dd").text.strip()
            if dt not in EXCLUDED_KEYS:
                result[dt] = dd
        except:
            continue

    # 안내사항 div 따로 추출
    try:
        all_dt = driver.find_elements(By.CSS_SELECTOR, ".view_box_items dt")
        for dt in all_dt:
            if "안내사항" in dt.text:
                dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                guide_div = dd.find_element(By.CSS_SELECTOR, 'div[style*="white-space:pre-wrap"]')
                result["안내사항"] = guide_div.text.strip()
                break
    except:
        result["안내사항"] = ""

    return result

def run_seis_crawling():
    driver = webdriver.Chrome()
    driver.get("https://www.seis.or.kr/home/sub.do?menukey=7208")
    wait = WebDriverWait(driver, 10)

    # 서울 클릭
    seoul_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="서울"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", seoul_button)
    seoul_button.click()
    time.sleep(1)

    # 진행중 클릭
    state_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="진행중"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", state_button)
    state_button.click()
    time.sleep(1)

    # 검색 클릭
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn_primary") and contains(text(), "검색")]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
    search_button.click()
    time.sleep(1)

    results = []
    page = 1

    while True:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.board_data_box li li.subj')))
        title_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.board_data_box li li.subj')

        for idx in range(len(title_elements)):
            title_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.board_data_box li li.subj')
            title_text = title_elements[idx].text.strip()

            print(f"[{len(results)+1}] {title_text} → 상세 진입 중...")
            driver.execute_script("arguments[0].scrollIntoView(true);", title_elements[idx])
            title_elements[idx].click()

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".view_box_items")))
            time.sleep(0.5)

            parsed = parse_detail_page(driver)

            # 현재 URL 따오기
            current_url = driver.current_url

            # 신청 기간 분리
            period_raw = parsed.get("게시기간", parsed.get("공고기간", parsed.get("접수기간", "")))
            start_date, end_date = parse_period(period_raw)

            # 결과 저장
            result = {
                "공고 제목": title_text,
                "주관기관": parsed.get("수행기관", "미정"),
                "신청 시작일": start_date,
                "신청 종료일": end_date,
                "카테고리": "사회적경제",
                "상세 내용": parsed.get("안내사항", "안내사항 없음"),
                "연결 링크": current_url,
            }

            results.append(result)

            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.board_data_box li li.subj')))

        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.bt_next')))
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            next_btn.click()
            page += 1
            time.sleep(1)
        except:
            print("📄 모든 페이지 완료")
            break

    driver.quit()
    return results

if __name__ == "__main__":
    results = run_seis_crawling()
    for r in results:
        print(r)
