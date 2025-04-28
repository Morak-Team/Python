# 📌 서울특별시 사회적경제지원센터 크롤러

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_sehub_crawling():
    driver = webdriver.Chrome()
    driver.get("https://sehub.net/archives/category/alarm/opencat")
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr")))
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

        # ✅ inform 제외 + td.title에 a태그가 있는 것만 필터링
        normal_rows = [
            row for row in rows
            if "inform" not in row.get_attribute("class") and row.find_elements(By.CSS_SELECTOR, "td.title a")
        ]

        print(f"🚨 총 {len(normal_rows)}건 발견 (inform 및 링크 없는 항목 제외)")

        for idx, row in enumerate(normal_rows[:10]):  # 최대 10개
            try:
                # 링크, 제목 추출
                title_element = row.find_element(By.CSS_SELECTOR, "td.title a")
                title_text = title_element.text.strip()
                detail_link = title_element.get_attribute("href")

                # 작성일 추출
                written_element = row.find_element(By.CSS_SELECTOR, "td.written")
                written_date = written_element.text.strip()

                # 상세페이지 새 탭 열기
                driver.execute_script("window.open(arguments[0]);", detail_link)
                driver.switch_to.window(driver.window_handles[-1])

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.singleTitle h2")))
                time.sleep(0.5)

                # ✅ 상세페이지 데이터 추출
                try:
                    title_detail = driver.find_element(By.CSS_SELECTOR, "div.th12 h2").text.strip()
                except:
                    title_detail = title_text  # fallback

                try:
                    agency_info = driver.find_element(By.XPATH, '//li[contains(text(), "주최/주관")]').text
                    agency = agency_info.split("주최/주관 :")[-1].strip()
                except:
                    agency = "상세 링크 참고"

                start_date = written_date if written_date else "상세 링크 참고"
                end_date = "상세 링크 참고"
                announcement_type = "사회적경제 공지"
                category = "사회적경제"

                try:
                    poster_img = driver.find_element(By.CSS_SELECTOR, "div.poster img")
                    description = poster_img.get_attribute("src")
                except:
                    description = "상세 링크 참고"

                results.append({
                    "공고 제목": title_detail,
                    "주관기관": agency,
                    "신청 시작일": start_date,
                    "신청 종료일": end_date,
                    "공고 유형": announcement_type,
                    "카테고리": category,
                    "상세 내용": description,
                    "연결 링크": detail_link
                })

                print(f"📄 [{idx+1}] {title_detail} 수집 완료!")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ [{idx+1}] 수집 실패: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    except Exception as e:
        print(f"❌ 전체 실패: {e}")

    finally:
        driver.quit()

    # ✅ 최종 결과 출력
    print("\n📄 최종 수집 결과:")
    for res in results:
        print(res)

    return results

if __name__ == "__main__":
    run_sehub_crawling()
