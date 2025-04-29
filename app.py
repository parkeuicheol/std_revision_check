import streamlit as st
import pandas as pd
import requests
from PIL import Image

def fetch_url_key(std_code: str) -> str:
    url = f"https://www.astm.org/Standards/{std_code}.htm"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.url.rstrip("/").split("/")[-1].split(".")[0]

# 0) 상단 이미지
img = Image.open("header.jpg")
st.image(img, use_container_width=True)

st.title("ASTM URL Key 기준 Revision 확인")
st.write("""
- 업로드할 Excel 파일의 첫 번째 시트에  
  `Standard Name` 과 `Current Revision URL Key`  
  두 개의 컬럼(header)이 반드시 있어야 합니다.
""")

# 1) 엑셀 업로드
uploaded_file = st.file_uploader("Upload your .xlsx file", type=["xlsx"])
if not uploaded_file:
    st.warning("엑셀 파일을 업로드해주세요.")
    st.stop()

df = pd.read_excel(uploaded_file)
st.subheader("업로드된 데이터")
st.dataframe(df, use_container_width=True)

if st.button("Run"):
    latest_keys    = []
    revision_flags = []

    for name, current_key in zip(df["Standard Name"], df["Current Revision URL Key"]):
        code = name.split()[1]  # e.g. "ASTM E45" → "E45"
        try:
            latest_key = fetch_url_key(code)
        except:
            latest_key = "Error"
        latest_keys.append(latest_key)

        # 같으면 "개정No", 다르면 "개정Yes"
        flag = "개정No" if latest_key.lower() == current_key.lower() else "개정Yes"
        revision_flags.append(flag)

    df["Latest Revision URL Key"] = latest_keys
    df["Revision YN"]              = revision_flags

    # 2) 스타일 함수 정의
    def highlight_revision(cell):
        return "background-color: red; color: white" if cell == "개정Yes" else ""

    # 3) Styler 적용
    styled = (
        df.style
          .applymap(highlight_revision, subset=["Revision YN"])
          .set_properties(**{"text-align": "center"})  # 전체 가운데 정렬 예시
    )

    st.subheader("비교 결과")
    st.dataframe(styled, use_container_width=True)
