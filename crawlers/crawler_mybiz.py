# 📌 네이버파이낸셜 마이비즈 크롤러
# GPT로 상세내용 다듬기 필요

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_mybiz_crawling():
    driver = webdriver.Chrome()
    driver.get("https://mybiz.pay.naver.com/subvention/search")
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        # 필터 클릭: 지역
        region_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '지역')]")))
        region_filter.click()
        print("✅ 지역 필터 열기 완료")

        seoul_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '서울특별시')]")))
        seoul_button.click()
        print("✅ 서울특별시 선택 완료")

        time.sleep(1)

        # 필터 클릭: 우대사항
        preference_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '우대사항')]")))
        preference_filter.click()
        print("✅ 우대사항 필터 열기 완료")

        time.sleep(1)

        # 사회적기업(인증) 클릭
        try:
            social_enterprise_div = driver.find_element(By.XPATH, "//div[contains(text(), '사회적기업(인증)')]")
            driver.execute_script("arguments[0].click();", social_enterprise_div)
            print("✅ 사회적기업(인증) 선택 완료")
        except Exception as e:
            print(f"❌ 사회적기업(인증) 클릭 실패: {e}")
            driver.quit()
            return

        time.sleep(2)

        # 스크롤 해서 공고 다 가져오기
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

        # 최대 10개까지만
        for idx, item in enumerate(items[:10], 1):
            try:
                link_element = item.find_element(By.CSS_SELECTOR, "a.guide_list_link")
                link = link_element.get_attribute("href")

                # 새탭 열고 이동
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])

                time.sleep(2)

                # 데이터 추출
                try:
                    title_detail = driver.find_element(By.CSS_SELECTOR, "p.detail_desc").text.strip()
                except:
                    title_detail = "상세 링크 참고"

                try:
                    org_detail = driver.find_element(By.CSS_SELECTOR, "span.mss_txt").text.strip()
                except:
                    org_detail = "상세 링크 참고"

                # 신청 시작일/종료일은 상세 링크 참고로 고정
                start_date = "상세 링크 참고"
                end_date = "상세 링크 참고"

                try:
                    tag_element = driver.find_element(By.CSS_SELECTOR, "li[class*='theme_']")
                    tag_text = tag_element.text.strip()
                except:
                    tag_text = "상세 링크 참고"

                try:
                    # 🔥 여기 수정: 3번째 guide_view_content_v2 안 p 태그
                    guide_sections = driver.find_elements(By.CSS_SELECTOR, "div.guide_view_content_v2")
                    if len(guide_sections) >= 3:
                        third_section = guide_sections[2]
                        p_tag = third_section.find_element(By.TAG_NAME, "p")
                        content_text = p_tag.text.strip()
                    else:
                        content_text = "상세 링크 참고"
                except:
                    content_text = "상세 링크 참고"

                results.append({
                    "공고 제목": title_detail,
                    "주관기관": org_detail,
                    "신청 시작일": start_date,
                    "신청 종료일": end_date,
                    "공고 유형": tag_text,
                    "상세 내용": content_text,
                    "연결 링크": link
                })

                print(f"📄 [{idx}] {title_detail} 수집 완료!")

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

if __name__ == "__main__":
    run_mybiz_crawling()
