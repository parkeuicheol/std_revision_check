# requirements:
# pip install streamlit pandas requests openpyxl

import streamlit as st
import pandas as pd
import requests

def fetch_url_key(std_code: str) -> str:
    url = f"https://www.astm.org/Standards/{std_code}.htm"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    final_url = resp.url
    return final_url.rstrip("/").split("/")[-1].split(".")[0]

st.title("ASTM URL Key 기준 Revision 확인")

st.write("""
- 업로드할 Excel 파일의 첫 번째 시트에
  `Standard Name` 과 `Current Revision URL Key`  
  두 개의 컬럼(header)이 반드시 있어야 합니다.
""")

# 1) Excel에서 데이터 불러오기
uploaded_file = st.file_uploader("Upload your .xlsx file", type=["xlsx"])
if uploaded_file is None:
    st.warning("엑셀 파일을 업로드해주세요.")
    st.stop()

# pandas로 읽어들여 바로 df 로 사용
df = pd.read_excel(uploaded_file)
st.subheader("업로드된 데이터")
st.dataframe(df, use_container_width=True)

if st.button("Run"):
    latest_keys     = []
    revision_flags  = []

    for name, current_key in zip(df["Standard Name"], df["Current Revision URL Key"]):
        # e.g. name="ASTM E45" → code="E45"
        code = name.split()[1]

        try:
            latest_key = fetch_url_key(code)
        except Exception as e:
            latest_key = f"Error"
        latest_keys.append(latest_key)

        flag = "개정No" if latest_key.lower() == current_key.lower() else "개정Yes"
        revision_flags.append(flag)

    df["Latest Revision URL Key"] = latest_keys
    df["Revision YN"]              = revision_flags

    st.subheader("비교 결과")
    st.dataframe(df, use_container_width=True)