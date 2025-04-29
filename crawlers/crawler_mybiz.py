# 📌 네이버파이낸셜 마이비즈 크롤러

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()
api_key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key=api_key)

# ✅ ChatGPT 요약 함수
def summarize_text_with_chatgpt(title, text):
    try:
        prompt = f"""
        다음 텍스트를 읽고, 친절하고 부드러운 서비스 직원처럼 자연스럽게 핵심만 요약해줘.

        - 말투는 토스나 카카오뱅크처럼 편안하고 친근해야 해.
        - 사무적인 표현은 쓰지 말고, 자연스럽고 간결하게 이어지게 써줘.
        - "안녕하세요" 같은 인삿말 없이, "이번 사업" 같은 표현 없이, **공고 제목을 자연스럽게 첫 문장에 언급해서** 시작해줘.
        - 문장은 부드럽고 자연스럽게 이어지도록 써줘.
        - "요약입니다:" 같은 말은 절대 쓰지 말고,
        - 읽기 편하게 문단 단위로 자연스럽게 끊어줘.
        - 마지막 문장은 항상 "자세한 내용은 상세 링크를 확인해 주세요."로 부드럽게 마무리해줘.

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

# ✅ 상세페이지 본문 + 테이블 모두 긁기
def get_full_content(driver):
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, "div.guide_view_content_v2")
        all_texts = []

        for section in sections:
            for header_tag in ["h3", "h4"]:
                try:
                    header = section.find_element(By.TAG_NAME, header_tag)
                    if header.text.strip():
                        all_texts.append(f"## {header.text.strip()}")
                except:
                    continue

            for text_tag in ["p", "li"]:
                texts = section.find_elements(By.TAG_NAME, text_tag)
                for text in texts:
                    if text.text.strip():
                        all_texts.append(text.text.strip())

            tables = section.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    row_text = " | ".join(col.text.strip() for col in cols if col.text.strip())
                    if row_text:
                        all_texts.append(row_text)

        full_content = "\n".join(all_texts)
        return full_content if full_content else "상세 링크 참고"

    except Exception as e:
        print(f"❌ 상세 내용 수집 실패: {e}")
        return "상세 링크 참고"

# ✅ 날짜 포맷 정리 함수 (ex: 2022.03.04 → 2022-03-04)
def clean_date_format(date_str):
    try:
        if "." in date_str:
            parts = date_str.split(".")
            if len(parts) == 3:
                year, month, day = parts
                return f"{year.strip()}-{month.strip().zfill(2)}-{day.strip().zfill(2)}"
    except:
        pass
    return date_str

# ✅ 메인 크롤러
def run_mybiz_crawling():
    driver = webdriver.Chrome()
    driver.get("https://mybiz.pay.naver.com/subvention/search")
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        # 🔥 팝업이 있으면 사라질 때까지 기다림
        try:
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "pop_img")))
            print("✅ 로딩 오버레이(pop_img) 사라짐 확인 완료")
        except:
            print("⚠️ pop_img가 없거나 바로 진행합니다")

        # 지역 필터 클릭
        region_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '지역')]")))
        region_filter.click()
        print("✅ 지역 필터 열기 완료")

        seoul_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '서울특별시')]")))
        seoul_button.click()
        print("✅ 서울특별시 선택 완료")
        time.sleep(1)

        # 우대사항 필터 클릭
        preference_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '우대사항')]")))
        preference_filter.click()
        print("✅ 우대사항 필터 열기 완료")
        time.sleep(1)

        try:
            social_enterprise_div = driver.find_element(By.XPATH, "//div[contains(text(), '사회적기업(인증)')]")
            driver.execute_script("arguments[0].click();", social_enterprise_div)
            print("✅ 사회적기업(인증) 선택 완료")
        except Exception as e:
            print(f"❌ 사회적기업(인증) 클릭 실패: {e}")
            driver.quit()
            return

        time.sleep(2)

        # 스크롤 해서 공고 모두 로딩
        prev_count = 0
        for scroll_try in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            items = driver.find_elements(By.CSS_SELECTOR, "li.guide_list_item")
            if len(items) == prev_count:
                break
            prev_count = len(items)
            print(f"⬇️ 스크롤 {scroll_try+1}회 완료 (현재 {len(items)}개)")

        items = driver.find_elements(By.CSS_SELECTOR, "li.guide_list_item")
        print(f"\n🚨 총 {len(items)}건 공고 발견\n")

        for idx, item in enumerate(items[:3], 1):
            try:
                link_element = item.find_element(By.CSS_SELECTOR, "a.guide_list_link")
                link = link_element.get_attribute("href")

                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)

                try:
                    title_detail = driver.find_element(By.CSS_SELECTOR, "p.detail_desc").text.strip()
                except:
                    title_detail = "상세 링크 참고"

                try:
                    org_detail = driver.find_element(By.CSS_SELECTOR, "span.mss_txt").text.strip()
                except:
                    org_detail = "상세 링크 참고"

                start_date = "상세 링크 참고"

                # 🔥 신청 종료일 추출 및 포맷 변환
                try:
                    end_date = "상세 링크 참고"
                    dts = driver.find_elements(By.CSS_SELECTOR, "dl dt")
                    for dt in dts:
                        if "접수 마감일" in dt.text:
                            dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                            first_span = dd.find_element(By.CSS_SELECTOR, "span.font_num")
                            raw_end_date = first_span.text.strip()
                            end_date = clean_date_format(raw_end_date)
                            break
                except Exception as e:
                    print(f"❌ 신청 종료일 수집 실패: {e}")
                    end_date = "상세 링크 참고"

                try:
                    tag_element = driver.find_element(By.CSS_SELECTOR, "li[class*='theme_']")
                    tag_text = tag_element.text.strip()
                except:
                    tag_text = "상세 링크 참고"

                full_content = get_full_content(driver)
                summarized_text = summarize_text_with_chatgpt(title_detail, full_content)

                results.append({
                    "공고 제목": title_detail,
                    "주관기관": org_detail,
                    "신청 시작일": start_date,
                    "신청 종료일": end_date,
                    "공고 유형": tag_text,
                    "상세 내용": summarized_text,
                    "연결 링크": link
                })

                print(f"📄 [{idx}] {title_detail} 수집 및 요약 완료!")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ [{idx}] 처리 중 오류: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    except Exception as e:
        print(f"❌ 전체 프로세스 실패: {e}")

    finally:
        driver.quit()

    print("\n📄 최종 수집 결과:")
    for res in results:
        print(res)

    return results

# ✅ 실행
if __name__ == "__main__":
    run_mybiz_crawling()
