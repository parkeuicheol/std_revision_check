# requirements:
# pip install streamlit pandas requests openpyxl

import streamlit as st
import pandas as pd
import requests
from PIL import Image

# Streamlit 페이지 설정: 반드시 다른 st.* 호출보다 먼저!
st.set_page_config(
    page_title="ASTM Standards Revision Comparator",
    layout="wide"
)

# ─── 0) 설정(구글 스프레드시트 CSV URL) ────────────────────
# 공유 설정을 “링크 있는 모든 사용자에게 보기 권한”으로 해두세요.
SPREADSHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "124a7g9IsLLZTVGfsHez--paBj8EU9ZWT"
    "/export?format=csv"
)

# 상단에 원본 Sheet URL 상수로 정의
SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "124a7g9IsLLZTVGfsHez--paBj8EU9ZWT"
    "/edit?usp=sharing"
)

def fetch_url_key(std_code: str) -> str:
    url = f"https://www.astm.org/Standards/{std_code}.htm"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.url.rstrip("/").split("/")[-1].split(".")[0]

# ─── 1) 상단 이미지 ─────────────────────────────────────────
img = Image.open("header.jpg")
st.image(img, use_container_width=True)

st.title("🔄 ASTM Standards Revision Check")
st.markdown(
    """
    **사용법**  
    1. 아래 링크로 구글 스프레드시트 원본(현보유 규격별 Revision정보)을 확인할 수 있습니다.
    2. 각 표준별 최신 Revision정보를 ASTM 웹사이트에서 가져와 규격별 Revision여부를 확인하고 결과를 표로 보여드립니다.
    """
    )
# st.write("""
# - 미리 지정한 Google Spreadsheet에서  
#   `Standard Name` 과 `Current Revision URL Key`  
#   두 개의 컬럼(header)을 자동으로 불러와 비교합니다.
# """)

# 클릭하면 원본 시트로 이동하는 링크
st.markdown(f"- 📋 **원본 스프레드시트 열기:** [여기를 클릭하세요]({SPREADSHEET_URL})")

# ─── 2) 구글 시트에서 데이터 로드 ────────────────────────────
try:
    df = pd.read_csv(SPREADSHEET_CSV_URL)
except Exception as e:
    st.error(f"스프레드시트에서 데이터를 가져오는 데 실패했습니다:\n{e}")
    st.stop()

st.subheader("♣현재 보유한 규격별 Revision정보♣")
st.dataframe(df, use_container_width=True)

# ─── 3) Run 버튼 & Progress Bar ────────────────────────────
if st.button("Run"):
    total = len(df)
    progress = st.progress(0)
    status_text = st.empty()

    latest_keys    = []
    revision_flags = []

    for i, (name, current_key) in enumerate(zip(
        df["Standard Name"],
        df["Current Revision URL Key"]
    )):
        status_text.text(f"({i+1}/{total}) 처리 중: {name}")
        try:
            code = name.split()[1]      # "ASTM E45" → "E45"
            latest_key = fetch_url_key(code)
        except Exception:
            latest_key = "Error"

        latest_keys.append(latest_key)
        flag = (
            "개정No"
            if latest_key.lower() == current_key.lower()
            else "개정Yes"
        )
        revision_flags.append(flag)
        progress.progress((i+1) / total)

    status_text.text("완료되었습니다! 🎉")

    # 결과 DataFrame 구성
    df["Latest Revision URL Key"] = latest_keys
    df["Revision YN"]              = revision_flags

    # 강조용 스타일링
    def highlight(cell):
        return "background-color: red; color: white" if cell == "개정Yes" else ""

    styled = (
        df.style
          .applymap(highlight, subset=["Revision YN"])
          .set_properties(**{"text-align": "center"})
    )

    st.subheader("비교 결과")
    st.dataframe(styled, use_container_width=True)
