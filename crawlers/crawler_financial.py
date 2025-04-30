from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def crawl_kinfa_social_finance():

    # ✅ GitHub Actions에서 충돌 없는 Chrome 옵션 구성
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # ✅ user-data-dir 충돌 방지: 아예 생략 (또는 임시 경로 할당도 가능)

    driver = webdriver.Chrome(options=options)  # ✅ 수정된 부분

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    url = "https://www.kinfa.or.kr/financialProduct/socialFinanceGlance.do"
    driver.get(url)

    try:
        # 사회적기업 체크
        social_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='사회적기업']")))
        social_button.click()
        print("✅ 사회적기업 체크 완료")
        time.sleep(1)

        # 내게 맞는 상품 검색하기 클릭
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "loanProductSearch")))
        search_button.click()
        print("✅ 상품 검색 클릭 완료")
        time.sleep(2)

        # 스크롤 해서 항목들 더 불러오기
        prev_count = 0
        for _ in range(5):  # 최대 5번 스크롤
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            cards = driver.find_elements(By.CSS_SELECTOR, "div.card-main")
            if len(cards) == prev_count:
                break
            prev_count = len(cards)
        print(f"✅ 총 {len(cards)}개 카드 발견")

        results = []

        for idx in range(len(cards)):
            try:
                # 다시 요소를 찾아야 함 (StaleElementException 방지)
                detail_buttons = driver.find_elements(By.CSS_SELECTOR, "a.learnMorePopup")
                wait.until(EC.element_to_be_clickable(detail_buttons[idx]))
                driver.execute_script("arguments[0].click();", detail_buttons[idx])
                print(f"✅ [{idx+1}] 카드 클릭 완료")

                # 팝업 제목 요소 존재 기다리기
                title_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-detail-left p.tit-01"))
                )

                # 텍스트가 들어올 때까지 추가 대기
                WebDriverWait(driver, 10).until(lambda d: title_elem.text.strip() != "")

                # 제목, 지원대상, 분류 가져오기
                title = title_elem.text.strip()
                info_items = driver.find_elements(By.CSS_SELECTOR, "div.big-number ul li")
                category = info_items[0].find_elements(By.TAG_NAME, "span")[1].text.strip()  # 분류
                target = info_items[1].find_elements(By.TAG_NAME, "span")[1].text.strip()    # 지원대상

                results.append({
                    "제목": title,
                    "분류": category,
                    "지원대상": target,
                })

                print(f"📄 [{idx+1}] {title} 저장 완료")

                # 팝업 닫기
                close_button = driver.find_element(By.CSS_SELECTOR, "div.product-detail button[title='닫기']")
                driver.execute_script("arguments[0].click();", close_button)
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ [{idx+1}] 에러 발생: {e}")
                try:
                    # 혹시 팝업 열려있으면 닫기
                    close_buttons = driver.find_elements(By.CSS_SELECTOR, "div.product-detail button[title='닫기']")
                    if close_buttons:
                        driver.execute_script("arguments[0].click();", close_buttons[0])
                        time.sleep(1)
                except:
                    pass
                continue

    except Exception as e:
        print(f"❌ 전체 프로세스 실패: {e}")
    finally:
        driver.quit()

    print("\n✅ 최종 결과:")
    for item in results:
        print(item)

    return results

# 실행
if __name__ == "__main__":
    crawl_kinfa_social_finance()
