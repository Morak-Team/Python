# 📌 사회연대은행 크롤러
# 📌 BSS 소상공인/사회적경제기업 모집중 공고 크롤러

# 📌 사회연대은행 크롤러
# 📌 BSS 소상공인/사회적경제기업 모집중 공고 크롤러

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_bss_crawling():
    driver = webdriver.Chrome()
    driver.get("https://www.bss.or.kr/business-apply/")
    wait = WebDriverWait(driver, 10)

    results = []

    try:
        # ✅ 체크박스 클릭: 소상공인
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.checkbox-list label")))
        labels = driver.find_elements(By.CSS_SELECTOR, "div.checkbox-list label")
        for label in labels:
            label_text = label.text.strip()
            if "소상공인" in label_text:
                input_element = label.find_element(By.TAG_NAME, "input")
                if not input_element.is_selected():
                    driver.execute_script("arguments[0].click();", input_element)
                    print(f"✅ {label_text} 체크 완료")
                break

        time.sleep(2)

        # ✅ 체크박스 클릭: 사회적경제기업 및 소셜벤처
        labels = driver.find_elements(By.CSS_SELECTOR, "div.checkbox-list label")
        for label in labels:
            label_text = label.text.strip()
            if "사회적경제기업 및 소셜벤처" in label_text:
                input_element = label.find_element(By.TAG_NAME, "input")
                if not input_element.is_selected():
                    driver.execute_script("arguments[0].click();", input_element)
                    print(f"✅ {label_text} 체크 완료")
                break

        time.sleep(3)

        # ✅ 스크롤 끝까지
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # ✅ 카드 가져오기
        items = driver.find_elements(By.CSS_SELECTOR, "a.box-gallery-list")
        print(f"🚨 총 {len(items)}건 후보 발견")

        # ✅ 소상공인 모집중 필터링
        valid_items = []
        for item in items:
            try:
                status_element = item.find_element(By.CSS_SELECTOR, "div.status")
                status_text = status_element.text.strip()

                category_element = item.find_element(By.CSS_SELECTOR, "p.elementor-heading-title")
                category_text = category_element.text.strip()

                if status_text == "모집중" and "소상공인" in category_text:
                    valid_items.append(item)
            except Exception:
                continue

        print(f"🎯 최종 유효 후보: {len(valid_items)}건")

        # ✅ 상세페이지 수집
        for idx, item in enumerate(valid_items, 1):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", item)

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.elementor-element-c381fd7")))
                time.sleep(0.5)

                # ✅ 공고 제목
                try:
                    title_element = driver.find_element(By.CSS_SELECTOR, "div.elementor-element-f91bfde p")
                    title_text = title_element.text.strip()
                except:
                    title_text = "상세 링크 참고"

                # ✅ 카테고리
                try:
                    category_element = driver.find_element(By.CSS_SELECTOR, "div.elementor-element-c381fd7 span")
                    category_text = category_element.text.strip()
                except:
                    category_text = "상세 링크 참고"

                # ✅ 공고 유형
                try:
                    type_element = driver.find_element(By.CSS_SELECTOR, "div.elementor-element-9468850 p")
                    type_text = type_element.text.strip()
                except:
                    type_text = "상세 링크 참고"

                # ✅ 신청 시작일
                try:
                    date_element = driver.find_element(By.CSS_SELECTOR, "li.elementor-icon-list-item time")
                    start_date = date_element.text.strip()
                except:
                    start_date = "상세 링크 참고"

                detail_url = driver.current_url

                # ✅ 공고 상세 내용 설명 (이미지 링크)
                try:
                    image_element = driver.find_element(By.CSS_SELECTOR, "figure.wp-block-image img")
                    image_url = image_element.get_attribute("src")
                except:
                    image_url = "상세 링크 참고"

                # ✅ 결과 정리
                result = {
                    "공고 제목": title_text,
                    "주관기관": "상세 링크 참고",
                    "신청 시작일": start_date,
                    "신청 종료일": "상세 링크 참고",
                    "공고 유형": type_text,
                    "카테고리": category_text,
                    "상세 내용": image_url,
                    "연결 링크": detail_url
                }

                results.append(result)
                print(f"📄 [{idx}] {title_text} 수집 완료!")

                driver.back()
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.box-gallery-list")))
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ [{idx}] 처리 중 오류: {e}")
                driver.get("https://www.bss.or.kr/business-apply/")
                time.sleep(3)
                continue

    except Exception as e:
        print(f"❌ 크롤링 전체 실패: {e}")
    finally:
        driver.quit()
        

    # ✅ 최종 결과 출력
    print("\n📄 최종 수집 결과:")
    for res in results:
        print(res)

    return results

if __name__ == "__main__":
    run_bss_crawling()