# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from openai import OpenAI
# from dotenv import load_dotenv
# import pandas as pd
# import os
# import json
# import re
# from typing import List
# from fastapi.middleware.cors import CORSMiddleware


# # 환경 설정
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

# # FastAPI 앱 초기화
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 또는 ["http://localhost:5173"] 등으로 제한 가능
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 엑셀 데이터 로딩
# base_dir = os.path.dirname(os.path.abspath(__file__))
# excel_path = os.path.join(base_dir, "../data/financialData.xlsx")
# df = pd.read_excel(excel_path)

# # 상품 요약 함수
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

# # 사용자 요청 모델
# class UserInput(BaseModel):
#     업종: str
#     기업_형태: str
#     기업_규모: str
#     연매출: str
#     필요금액: str
#     선호_이율_구조: str
#     담보_제공_가능_여부: str
#     필요_서비스_종류: str
#     우대_조건_보유_항목: List[str]

# # API 엔드포인트
# @app.post("/recommend")
# def recommend(user_input: UserInput):
#     try:
#         user_info = "\n".join([
#             f"- 업종: {user_input.업종}",
#             f"- 기업 형태: {user_input.기업_형태}",
#             f"- 기업 규모: {user_input.기업_규모}",
#             f"- 연매출: {user_input.연매출}",
#             f"- 필요금액: {user_input.필요금액}",
#             f"- 선호 이율 구조: {user_input.선호_이율_구조}",
#             f"- 담보 제공 가능 여부: {user_input.담보_제공_가능_여부}",
#             f"- 필요 서비스 종류: {user_input.필요_서비스_종류}",
#             f"- 우대 조건 보유 항목: {', '.join(user_input.우대_조건_보유_항목)}"
#         ])

#         # 프롬프트 구성
#         prompt = f"""
# 당신은 사회적경제에 특화된 금융 추천 챗봇입니다.

# - 말투는 토스나 카카오뱅크처럼 부드럽고 친근하게
# - 사용자에게 가장 적합한 금융 상품 1개를 아래 포맷에 따라 추천해주세요.
# - 사용자의 업종/형태/규모/우대조건/필요금액을 고려해 **아래 상품 중 조건과 가장 많이 일치하는 1개**를 골라주세요.
# - 단순히 보편적으로 인기 있는 상품(예: 사회적기업 나눔보증 등)은 피하고, **사용자 상황과 가장 잘 부합하는 상품을 골라야** 합니다.

# [응답 포맷]
# 상품명: {{상품명}}
# 주관기관: {{기관명}}
# 추천이유: {{친근한 설명 포함 상세 설명}}
# 마무리: {{조건에 따라 적절한 클로징 멘트}}

# [사용자 정보]
# {user_info}

# [금융 상품 목록 요약] (총 {len(df)}개)
# {product_summaries}

# 사용자에게 가장 적합한 금융 상품을 추천하고 위의 포맷대로 작성해주세요.
# """

#         # GPT 호출
#         response = client.chat.completions.create(
#             model="gpt-4-1106-preview",
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         content = response.choices[0].message.content.strip()

#         # GPT 응답 파싱
#         title_match = re.search(r"상품명:\s*(.+)", content)
#         agency_match = re.search(r"주관기관:\s*(.+)", content)
#         reason_match = re.search(r"추천이유:\s*(.+?)(마무리:|$)", content, re.DOTALL)
#         closing_match = re.search(r"마무리:\s*(.+)", content, re.DOTALL)

#         if not (title_match and agency_match and reason_match and closing_match):
#             raise ValueError("GPT 응답 형식이 예상과 다릅니다.")

#         return {
#             "product": {
#                 "title": title_match.group(1).strip(),
#                 "agency": agency_match.group(1).strip(),
#                 "description": reason_match.group(1).strip()
#             },
#             "closing": closing_match.group(1).strip()
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from openai import OpenAI
# from dotenv import load_dotenv
# import pandas as pd
# import os
# import json
# import re
# from typing import List
# from fastapi.middleware.cors import CORSMiddleware

# # 환경 설정
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

# # FastAPI 앱 초기화
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 엑셀 데이터 로딩
# base_dir = os.path.dirname(os.path.abspath(__file__))
# excel_path = os.path.join(base_dir, "../data/financialData.xlsx")
# df = pd.read_excel(excel_path)


# # 🔍 필터링 함수 추가
# def filter_candidates(df, user_input):
#     def contains_case_insensitive(text, keyword):
#         return keyword.lower() in str(text).lower()

#     condition1 = df["지원대상"].apply(lambda x: contains_case_insensitive(x, user_input.기업_형태))
#     condition2 = df["분류"].apply(lambda x: contains_case_insensitive(x, user_input.필요_서비스_종류))

#     filtered_df = df[condition1 | condition2]

#     # 너무 적으면 fallback으로 상위 N개 제공
#     if filtered_df.empty:
#         filtered_df = df.head(20)

#     return filtered_df


# # 요약 함수
# def summarize_product(row):
#     title = row["제목"]
#     category = row["분류"]
#     target = row["지원대상"]
#     agency = row["주관기관"]
#     method = row.get("신청방법(절차)", "신청 방법 정보 없음")
#     contact = row.get("문의처", "문의처 정보 없음")
#     summary = row["사업 개요"][:40].strip().replace("\n", " ")
#     return f"{title} ({category}, {target}) - {summary} / 주관: {agency}, 신청: {method}, 문의: {contact}"


# # 사용자 입력 모델
# class UserInput(BaseModel):
#     업종: str
#     기업_형태: str
#     기업_규모: str
#     연매출: str
#     필요금액: str
#     선호_이율_구조: str
#     담보_제공_가능_여부: str
#     필요_서비스_종류: str
#     우대_조건_보유_항목: List[str]


# # 추천 API
# @app.post("/recommend")
# def recommend(user_input: UserInput):
#     try:
#         # 1. 후보 상품 필터링
#         filtered_df = filter_candidates(df, user_input)

#         # 2. 상품 요약 텍스트 생성
#         product_summaries = "\n".join(filtered_df.apply(summarize_product, axis=1))

#         # 3. 사용자 정보 정리
#         user_info = "\n".join([
#             f"- 업종: {user_input.업종}",
#             f"- 기업 형태: {user_input.기업_형태}",
#             f"- 기업 규모: {user_input.기업_규모}",
#             f"- 연매출: {user_input.연매출}",
#             f"- 필요금액: {user_input.필요금액}",
#             f"- 선호 이율 구조: {user_input.선호_이율_구조}",
#             f"- 담보 제공 가능 여부: {user_input.담보_제공_가능_여부}",
#             f"- 필요 서비스 종류: {user_input.필요_서비스_종류}",
#             f"- 우대 조건 보유 항목: {', '.join(user_input.우대_조건_보유_항목)}"
#         ])

#         # 4. 프롬프트 구성
#         prompt = f"""
# 당신은 사회적경제에 특화된 금융 추천 챗봇입니다.

# - 말투는 토스나 카카오뱅크처럼 부드럽고 친근하게
# - 사용자에게 가장 적합한 금융 상품 1개를 아래 포맷에 따라 추천해주세요.

# [응답 포맷]
# 상품명: {{상품명}}
# 주관기관: {{기관명}}
# 추천이유: {{친근한 설명 포함 상세 설명}}
# 마무리: {{조건에 따라 적절한 클로징 멘트}}

# [사용자 정보]
# {user_info}

# [금융 상품 목록 요약] (총 {len(filtered_df)}개)
# {product_summaries}

# 사용자에게 가장 적합한 금융 상품을 추천하고 위의 포맷대로 작성해주세요.
# """

#         # 5. GPT 호출
#         response = client.chat.completions.create(
#             model="gpt-4-1106-preview",
#             messages=[{"role": "user", "content": prompt}]
#         )

#         content = response.choices[0].message.content.strip()

#         # 6. GPT 응답 파싱
#         title_match = re.search(r"상품명:\s*(.+)", content)
#         agency_match = re.search(r"주관기관:\s*(.+)", content)
#         reason_match = re.search(r"추천이유:\s*(.+?)(마무리:|$)", content, re.DOTALL)
#         closing_match = re.search(r"마무리:\s*(.+)", content, re.DOTALL)

#         if not (title_match and agency_match and reason_match and closing_match):
#             raise ValueError("GPT 응답 형식이 예상과 다릅니다.")

#         return {
#             "product": {
#                 "title": title_match.group(1).strip(),
#                 "agency": agency_match.group(1).strip(),
#                 "description": reason_match.group(1).strip()
#             },
#             "closing": closing_match.group(1).strip()
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# api/server.py
# api/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import re

# ──────────────────────── 환경설정 ────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 필요하면 ['http://localhost:5173'] 로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────── 데이터 로딩 ────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "../data/financialData.xlsx")
df         = pd.read_excel(EXCEL_PATH)

# ──────────────────────── 유틸 함수 ────────────────────────
def contains(text: str, keyword: str) -> bool:
    return keyword.lower() in str(text).lower()

def filter_candidates(df: pd.DataFrame, ui) -> pd.DataFrame:
    cond1 = df["지원대상"].apply(lambda x: contains(x, ui.기업_형태))
    cond2 = df["분류"].apply(lambda x: contains(x, ui.필요_서비스_종류))
    sub   = df[cond1 | cond2]
    return sub if not sub.empty else df.head(30)  # fallback 최대 30개

def summarize(row):
    return (
        f"{row['제목']} ({row['분류']}, {row['지원대상']}) - "
        f"{row['사업 개요'][:40].strip().replace(chr(10),' ')} "
        f"/ 주관: {row['주관기관']}, 신청: {row.get('신청방법(절차)', '정보 없음')}, "
        f"문의: {row.get('문의처','정보 없음')}"
    )

# ──────────────────────── Pydantic 모델 ────────────────────────
class UserInput(BaseModel):
    업종: str
    기업_형태: str
    기업_규모: str
    연매출: str
    필요금액: str
    선호_이율_구조: str
    담보_제공_가능_여부: str
    필요_서비스_종류: str
    우대_조건_보유_항목: List[str]

# ──────────────────────── 스타일 가이드 ────────────────────────
STYLE_GUIDE = """
[스타일 가이드]
1) 토스·카카오뱅크 알림처럼 짧고 캐주얼한 톤 (“~요” 종결)
2) 한 문단 길이 3~5줄, 이모지 1~2개 허용 😊🌱
3) 숫자는 ‘5천만원’ 같이 한글로 표기
"""

# ──────────────────────── API 엔드포인트 ────────────────────────
@app.post("/recommend")
def recommend(ui: UserInput):
    try:
        # 1. 후보 상품 추리기
        cand_df = filter_candidates(df, ui)
        prod_txt = "\n".join(cand_df.apply(summarize, axis=1))

        # 2. 사용자 정보 포맷
        ui_txt = "\n".join([
            f"- 업종: {ui.업종}",
            f"- 기업 형태: {ui.기업_형태}",
            f"- 기업 규모: {ui.기업_규모}",
            f"- 연매출: {ui.연매출}",
            f"- 필요금액: {ui.필요금액}",
            f"- 선호 이율 구조: {ui.선호_이율_구조}",
            f"- 담보 제공 가능 여부: {ui.담보_제공_가능_여부}",
            f"- 필요 서비스 종류: {ui.필요_서비스_종류}",
            f"- 우대 조건 보유 항목: {', '.join(ui.우대_조건_보유_항목)}",
        ])

        # 3. 프롬프트
        prompt = f"""{STYLE_GUIDE}

당신은 사회적경제 특화 금융추천 챗봇이에요.
아래 정보만 참고해서 ‘가장 잘 맞는 상품 1개’만 골라주세요.

[응답 포맷]
상품명: {{상품명}}
주관기관: {{기관}}
추천이유: {{짧고 캐주얼한 3~5줄}}
마무리: {{두 줄 이내 캐주얼 응원 멘트}}

[사용자 정보]
{ui_txt}

[후보 상품 요약] (총 {len(cand_df)}개)
{prod_txt}
"""

        # 4. GPT 호출
        res = client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0.6,                    # 표현 다양화
            messages=[{"role": "user", "content": prompt}],
        )
        content = res.choices[0].message.content.strip()

        # 5. 파싱
        title   = re.search(r"상품명:\s*(.+)", content)
        agency  = re.search(r"주관기관:\s*(.+)", content)
        reason  = re.search(r"추천이유:\s*(.+?)(?:마무리:|$)", content, re.S)
        closing = re.search(r"마무리:\s*(.+)", content, re.S)

        if not all([title, agency, reason, closing]):
            raise ValueError("GPT 응답 형식이 올바르지 않습니다.")

        return {
            "product": {
                "title": title.group(1).strip(),
                "agency": agency.group(1).strip(),
                "description": reason.group(1).strip()
            },
            "closing": closing.group(1).strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
