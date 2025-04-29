# requirements:
# pip install streamlit pandas requests openpyxl

import streamlit as st
import pandas as pd
import requests
from PIL import Image

def fetch_url_key(std_code: str) -> str:
    url = f"https://www.astm.org/Standards/{std_code}.htm"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.url.rstrip("/").split("/")[-1].split(".")[0]

# ─── 0) 상단 이미지 ─────────────────────────────────
img = Image.open("header.jpg")
st.image(img, use_container_width=True)

st.title("ASTM URL Key 기준 Revision 확인")
st.write("""
- 업로드할 Excel 파일의 첫 번째 시트에  
  `Standard Name` 과 `Current Revision URL Key`  
  두 개의 컬럼(header)이 반드시 있어야 합니다.
""")

# ─── 1) 엑셀 업로드 ─────────────────────────────────
uploaded_file = st.file_uploader("Upload your .xlsx file", type=["xlsx"])
if not uploaded_file:
    st.warning("엑셀 파일을 업로드해주세요.")
    st.stop()

df = pd.read_excel(uploaded_file)
st.subheader("업로드된 데이터")
st.dataframe(df, use_container_width=True)

# ─── 2) Run 버튼 & Progress Bar ────────────────────
if st.button("Run"):
    total = len(df)
    progress = st.progress(0)            # 0%부터 시작
    status_text = st.empty()             # 처리 중 상태 메시지를 찍을 곳

    latest_keys    = []
    revision_flags = []

    for i, (name, current_key) in enumerate(zip(df["Standard Name"], df["Current Revision URL Key"])):
        # 진행 상태 업데이트
        status_text.text(f"({i+1}/{total}) 처리 중: {name}")
        try:
            code = name.split()[1]      # "ASTM E45" → "E45"
            latest_key = fetch_url_key(code)
        except Exception:
            latest_key = "Error"

        latest_keys.append(latest_key)
        flag = "개정No" if latest_key.lower() == current_key.lower() else "개정Yes"
        revision_flags.append(flag)

        # progress bar 업데이트
        progress.progress((i+1) / total)

    # 완료 후 메시지
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
