from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def crawl_kinfa_social_finance():
    # Chrome headless 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    results = []

    try:
        # 1) 메인 페이지 접속 → 필터 적용 → 검색
        driver.get("https://www.kinfa.or.kr/financialProduct/socialFinanceGlance.do")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='사회적기업']"))).click()
        driver.find_element(By.ID, "loanProductSearch").click()
        time.sleep(2)

        main_window = driver.current_window_handle

        # 2) 1~4 페이지 순회
        for page in range(1, 5):
            print(f"\n▶ 페이지 {page} 크롤링 시작")

            # (1) page 버튼 클릭 (data-pageno 속성 이용)
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"button.item.paging[data-pageno='{page}']"))
            )
            driver.execute_script("arguments[0].click();", btn)

            # (2) 해당 버튼이 active 될 때까지 대기
            wait.until(lambda d: d.find_element(
                By.CSS_SELECTOR,
                f"button.item.paging.active[data-pageno='{page}']"
            ))
            time.sleep(1)

            # (3) 스크롤로 카드 로드
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            cards = driver.find_elements(By.CSS_SELECTOR, "div.card-main")
            print(f"  - 총 {len(cards)}개 카드 발견")

            # (4) 카드별 팝업 열고 데이터 추출
            for idx in range(len(cards)):
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, "a.learnMorePopup")
                    if idx >= len(buttons):
                        print(f"    ⚠️ [{idx+1}] 버튼 없음, 스킵")
                        continue

                    # 팝업 열기
                    driver.execute_script("arguments[0].click();", buttons[idx])
                    wait.until(lambda d: len(d.window_handles) > 1)
                    popup = [h for h in driver.window_handles if h != main_window][0]
                    driver.switch_to.window(popup)

                    # 로딩 스피너 사라질 때까지
                    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#loading.is_active")))

                    # 제목 추출
                    title = wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "p.tit-01"))
                    ).text.strip()

                    # 상세 항목 전부 추출
                    detail_items = driver.find_elements(
                        By.CSS_SELECTOR,
                        ".product-detail-left .big-number li, "
                        + ".product-detail-right ul.dlist-01 li, "
                        + ".sub-con ul.dlist-01-large li"
                    )

                    data = {"페이지": page, "제목": title}
                    for li in detail_items:
                        key = li.find_element(By.CSS_SELECTOR, "span.dt, span.tit").text.strip()
                        val = li.find_element(By.CSS_SELECTOR, "span.dd, span.txt").text.strip()
                        data[key] = val

                    results.append(data)
                    print(f"    ✅ [{idx+1}] '{title}' — {len(detail_items)}개 항목 저장")

                    # 팝업 닫고 메인으로 복귀
                    driver.close()
                    driver.switch_to.window(main_window)
                    time.sleep(0.5)

                except Exception as e:
                    print(f"    ⚠️ [{idx+1}] 오류: {e}")
                    # 팝업이 열려 있으면 닫고 복귀
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                        driver.switch_to.window(main_window)

        # 3) DataFrame 변환 후 엑셀로 저장
        df = pd.DataFrame(results)
        df.to_excel("results.xlsx", index=False)
        print("\n🎉 크롤링 완료! 'results.xlsx' 파일로 저장되었습니다.")

    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    crawl_kinfa_social_finance()
