# from openai import OpenAI
# import os
# from dotenv import load_dotenv
# import pandas as pd

# # 1. API 키 설정
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

# # 2. 엑셀 데이터 불러오기
# df = pd.read_excel("../data/financialData.xlsx")

# # 3. 전체 상품 데이터 간결 요약 (token 최적화)
# def summarize_product(row):
#     title = row['제목']
#     category = row['분류']
#     target = row['지원대상']
#     agency = row['주관기관']
#     method = row.get('신청방법(절차)', '신청 방법 정보 없음')
#     contact = row.get('문의처', '문의처 정보 없음')
#     summary = row['사업 개요'][:40].strip().replace("\n", " ")
#     return f"{title} ({category}, {target}) - {summary} / 주관: {agency}, 신청: {method}, 문의: {contact}"

# product_summaries = "\n".join(df.apply(summarize_product, axis=1))

# # 4. 사용자 입력 예시
# user_input = {
#     "업종": "소셜벤처",
#     "기업 형태": "사회적기업",
#     "기업 규모": "10인 미만",
#     "연매출": "2억",
#     "필요금액": "5천만원",
#     "선호 이율 구조": "고정금리",
#     "담보 제공 가능 여부": "불가능",
#     "필요 서비스 종류": "운영자금 대출",
#     "우대 조건 보유 항목": "없음"
# }
# user_info = "\n".join(f"- {k}: {v}" for k, v in user_input.items())

# # 5. 부드러운 말투 + 기관 정보 포함 + 챗봇성 마무리 프롬프트
# prompt = f"""
# 당신은 사회적경제에 특화된 금융 추천 챗봇입니다.

# 다음 지침을 지켜 사용자에게 금융 상품을 추천해주세요:

# - 말투는 토스나 카카오뱅크처럼 부드럽고 친근하게
# - 추천 이유에는 기업 형태, 규모, 이율 선호, 우대 조건 등과의 관련성을 포함
# - 각 상품에 주관기관, 신청 방법, 문의처 정보를 반드시 포함
# - 마지막 문단은 다음 기준에 따라 자연스럽게 마무리해주세요:

#   - 조건에 맞는 상품을 추천한 경우에는 다음 문구를 사용해주세요:

#     "두 상품 모두 사용자님의 조건에 잘 맞는 금융지원 상품이에요.  
#     자세한 내용은 각 주관기관을 통해 확인해보시면 좋아요.  
#     사회를 더 따뜻하게 만드는 이 길을 응원할게요.  
#     이 추천이 작게나마 힘이 되었으면 좋겠습니다!"

#   - 추천할 만한 상품이 없는 경우에는 다음 문구를 사용해주세요:

#     "조건에 꼭 맞는 금융상품은 현재 목록에는 없는 것 같아요.  
#     하지만 서민금융진흥원, 신용보증기금, 서울신용보증재단 같은 기관에서  
#     더 다양한 지원 정보를 찾아보시면 좋을 것 같아요.  
#     사회를 더 나은 방향으로 바꾸는 사용자님의 활동을 진심으로 응원합니다!"

# - 만약 아래 상품 목록 중 어떤 항목도 사용자 조건(예: 기업 형태, 업종, 우대 조건 등)에 명확히 일치하지 않는다면,
#   절대 추천하지 마세요. 억지로 비슷한 상품을 제안하지 마시고, 
#   현재 조건에 맞는 상품이 없다는 점을 사용자에게 솔직하고 친절하게 알려주세요.
# - 그리고 대안으로 조건에 맞는 정보를 얻을 수 있는 기관이나 포털(예: 서민금융진흥원, 신용보증기금, 서울신용보증재단 등)을 안내해 주세요.


# [사용자 정보]
# {user_info}

# [금융 상품 목록 요약] (총 {len(df)}개)
# {product_summaries}

# 이 사용자에게 가장 적합한 금융 상품 1개를 추천해주세요.
# """

# # 6. GPT 호출
# response = client.chat.completions.create(
#     model="gpt-4-1106-preview",  # 128k context
#     messages=[
#         {"role": "user", "content": prompt}
#     ]
# )

# # 7. 응답 출력
# print(response.choices[0].message.content)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import json
import re

# 환경 설정
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

# FastAPI 앱 초기화
app = FastAPI()

# 엑셀 데이터 로딩
df = pd.read_excel("../data/financialData.xlsx")

# 상품 요약 함수
def summarize_product(row):
    title = row['제목']
    category = row['분류']
    target = row['지원대상']
    agency = row['주관기관']
    method = row.get('신청방법(절차)', '신청 방법 정보 없음')
    contact = row.get('문의처', '문의처 정보 없음')
    summary = row['사업 개요'][:40].strip().replace("\n", " ")
    return f"{title} ({category}, {target}) - {summary} / 주관: {agency}, 신청: {method}, 문의: {contact}"

product_summaries = "\n".join(df.apply(summarize_product, axis=1))

# 사용자 요청 모델
class UserInput(BaseModel):
    업종: str
    기업_형태: str
    기업_규모: str
    연매출: str
    필요금액: str
    선호_이율_구조: str
    담보_제공_가능_여부: str
    필요_서비스_종류: str
    우대_조건_보유_항목: str

# API 엔드포인트
@app.post("/recommend")
def recommend(user_input: UserInput):
    try:
        user_info = "\n".join([
            f"- 업종: {user_input.업종}",
            f"- 기업 형태: {user_input.기업_형태}",
            f"- 기업 규모: {user_input.기업_규모}",
            f"- 연매출: {user_input.연매출}",
            f"- 필요금액: {user_input.필요금액}",
            f"- 선호 이율 구조: {user_input.선호_이율_구조}",
            f"- 담보 제공 가능 여부: {user_input.담보_제공_가능_여부}",
            f"- 필요 서비스 종류: {user_input.필요_서비스_종류}",
            f"- 우대 조건 보유 항목: {user_input.우대_조건_보유_항목}"
        ])

        # 프롬프트 구성
        prompt = f"""
당신은 사회적경제에 특화된 금융 추천 챗봇입니다.

- 말투는 토스나 카카오뱅크처럼 부드럽고 친근하게
- 사용자에게 가장 적합한 금융 상품 1개를 아래 포맷에 따라 추천해주세요.

[응답 포맷]
상품명: {{상품명}}
주관기관: {{기관명}}
추천이유: {{친근한 설명 포함 상세 설명}}
마무리: {{조건에 따라 적절한 클로징 멘트}}

[사용자 정보]
{user_info}

[금융 상품 목록 요약] (총 {len(df)}개)
{product_summaries}

사용자에게 가장 적합한 금융 상품을 추천하고 위의 포맷대로 작성해주세요.
"""

        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        # GPT 응답 파싱
        title_match = re.search(r"상품명:\s*(.+)", content)
        agency_match = re.search(r"주관기관:\s*(.+)", content)
        reason_match = re.search(r"추천이유:\s*(.+?)(마무리:|$)", content, re.DOTALL)
        closing_match = re.search(r"마무리:\s*(.+)", content, re.DOTALL)

        if not (title_match and agency_match and reason_match and closing_match):
            raise ValueError("GPT 응답 형식이 예상과 다릅니다.")

        return {
            "product": {
                "title": title_match.group(1).strip(),
                "agency": agency_match.group(1).strip(),
                "description": reason_match.group(1).strip()
            },
            "closing": closing_match.group(1).strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
