# 👾 기업마당 공공 API 

from dotenv import load_dotenv
import os
import requests
import re
from openai import OpenAI

# ✅ .env 파일 로드
load_dotenv()

API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
API_KEY = os.getenv("BIZ_INFO_API_KEY")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

# ✅ OpenAI 클라이언트 설정
client = OpenAI(api_key=OPEN_API_KEY)

params = {
    "crtfcKey": API_KEY,
    "dataType": "json",
    "hashtags": "서울",  # 서울 키워드
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

# ✅ 데이터 수집 함수
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

        # ✅ ChatGPT로 요약
        summarized_text = summarize_text_with_chatgpt(title, raw_summary)

        result = {
            "공고 제목": title,
            "주관기관": organization,
            "신청 시작일": start_date,
            "신청 종료일": end_date,
            "공고 유형": announce_type,
            "상세 내용": summarized_text,
            "연결 링크": link,
        }
        results.append(result)

    return results

# ✅ 실행
if __name__ == "__main__":
    results = fetch_bizinfo_data(limit=15)  # 🔥 20개 제한 적용
    for r in results:
        print(r)
