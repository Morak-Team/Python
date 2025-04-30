# 📌 사회적 기업 포털 크롤러
# GPT로 상세내용 다듬기 필요

# 📌 사회연대은행(사회적기업포털) 크롤러 + ChatGPT 요약 포함 버전

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
import openai
# ✅ OpenAI API 설정

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")
client = openai.OpenAI()

# ✅ 제외할 키들
EXCLUDED_KEYS = {
    "수행기관 구분", "담당부서", "담당자 및 연락처", "지원지역", "첨부파일", ""
}

# ✅ ChatGPT 요약 함수
def summarize_text_with_chatgpt(title, text):
    try:
        prompt = f"""
        다음 텍스트를 읽고, 친절하고 부드러운 서비스 직원처럼 자연스럽게 핵심만 요약해줘.

        - 말투는 토스나 카카오뱅크처럼 편안하고 친근해야 해.
        - 사무적인 표현은 쓰지 말고, 자연스럽고 간결하게 이어지게 써줘.
        - "안녕하세요" 같은 인삿말 없이, "이번 사업" 대신 반드시 공고 제목을 자연스럽게 언급해서 시작해줘.
        - 첫 문장은 "{title}에서는 ~ 지원하고 있어요" 또는 "{title}을 통해 ~을 도와드리고 있어요"처럼 자연스럽게 시작해줘.
        - 문장은 부드럽고 자연스럽게 연결되도록 써줘.
        - "요약입니다:" 같은 말은 절대 쓰지 말고,
        - 읽기 편하게 문단 단위로 자연스럽게 끊어줘.
        - 마지막에는 항상 "자세한 내용은 상세 링크를 확인해 주세요."로 부드럽게 마무리해줘.

        다음은 요약할 텍스트야:

        공고 제목: {title}
        본문 내용:
        {text}
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 친절하고 부드럽게 요약하는 전문 어시스턴트야."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"❌ ChatGPT 요약 실패: {e}")
        return "요약 실패"

# ✅ 기간 파싱 함수
def parse_period(period_text):
    """'2025-04-22 ~ 2025-05-09' 형태를 start, end로 나누는 함수"""
    if not period_text:
        return "미정", "미정"
    match = re.match(r"(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})", period_text)
    if match:
        return match.group(1), match.group(2)
    else:
        return "미정", "미정"

# ✅ 상세페이지 파싱 함수
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

    # 안내사항 따로 추출
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

# ✅ 메인 크롤러
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

            # 현재 URL
            current_url = driver.current_url

            # 신청 기간 분리
            period_raw = parsed.get("게시기간", parsed.get("공고기간", parsed.get("접수기간", "")))
            start_date, end_date = parse_period(period_raw)

            # 공고유형 가져오기
            announcement_type = parsed.get("공고유형", "상세 링크 참고")

            # 안내사항 텍스트 가져오기
            raw_detail_text = parsed.get("안내사항", "")

            # ✅ ChatGPT 요약
            summarized_text = summarize_text_with_chatgpt(title_text, raw_detail_text)

            # 결과 저장
            result = {
                "공고 제목": title_text,
                "주관기관": parsed.get("수행기관", "상세 링크 참고"),
                "신청 시작일": start_date,
                "신청 종료일": end_date,
                "공고 유형": announcement_type,
                "상세 내용": summarized_text,
                "연결 링크": current_url,
            }

            results.append(result)

            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.board_data_box li li.subj')))

        # 다음 페이지 버튼
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

# ✅ 실행
if __name__ == "__main__":
    results = run_seis_crawling()
    for r in results:
        print(r)
