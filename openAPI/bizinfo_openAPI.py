# 👾 기업마당 공공 API 
# GPT로 상세내용 다듬기 필요

from dotenv import load_dotenv
import os
import requests
import re

# .env 파일 로드
load_dotenv()

API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
API_KEY = os.getenv("BIZ_INFO_API_KEY")

params = {
    "crtfcKey": API_KEY,
    "dataType": "json",
    "hashtags": "서울",  # 서울 키워드
}

def parse_period(period_text):
    """20220727 ~ 20220930 형태를 2022-07-27, 2022-09-30으로 변환"""
    if not period_text:
        return "상세 링크 참고", "상세 링크 참고"
    match = re.match(r"(\d{8})\s*~\s*(\d{8})", period_text)
    if match:
        start = match.group(1)
        end = match.group(2)
        return f"{start[:4]}-{start[4:6]}-{start[6:]}", f"{end[:4]}-{end[4:6]}-{end[6:]}"
    else:
        return "상세 링크 참고", "상세 링크 참고"

def extract_first_p_text(html_text):
    """<p>...</p> 중 첫 번째 텍스트만 뽑는다"""
    if not html_text:
        return "상세 링크 참고"
    start_idx = html_text.find("<p>")
    end_idx = html_text.find("</p>", start_idx)
    if start_idx != -1 and end_idx != -1:
        return html_text[start_idx + 3:end_idx].strip()
    else:
        return "상세 링크 참고"

def fetch_bizinfo_data(limit=20):
    """기업마당 API로부터 데이터를 가져오고, 최대 limit개까지 반환"""
    res = requests.get(API_URL, params=params)
    res.raise_for_status()
    data = res.json()

    items = data.get("jsonArray", [])

    # 🔍 '서울' 포함된 공고만 필터링
    seoul_items = [
        item for item in items
        if any([
            "서울" in (item.get("jrsdInsttNm") or ""),
            "서울" in (item.get("excInsttNm") or ""),
            "서울" in (item.get("bsnsSumryCn") or ""),
            "서울" in (item.get("hashTags") or ""),
        ])
    ]

    print(f"✅ 총 {len(seoul_items)}건의 '서울' 관련 지원사업이 검색되었습니다.\n")

    # 📌 가져온 후 최대 limit개만 추출
    selected_items = seoul_items[:limit]

    results = []

    for item in selected_items:
        title = item.get("pblancNm", "상세 링크 참고")
        organization = item.get("jrsdInsttNm", "상세 링크 참고")
        period_text = item.get("reqstBeginEndDe") or item.get("reqstDt") or ""
        start_date, end_date = parse_period(period_text)
        announce_type = item.get("pldirSportRealmLclasCodeNm", "상세 링크 참고")
        link = "https://www.bizinfo.go.kr" + item.get("pblancUrl", "")

        raw_summary = item.get("bsnsSumryCn", "")
        summary = extract_first_p_text(raw_summary)

        result = {
            "공고 제목": title,
            "주관기관": organization,
            "신청 시작일": start_date,
            "신청 종료일": end_date,
            "공고 유형": announce_type,
            "상세 내용": summary,
            "연결 링크": link,
        }
        results.append(result)

    return results

if __name__ == "__main__":
    results = fetch_bizinfo_data(limit=20)  # 🔥 20개 제한 적용
    for r in results:
        print(r)
