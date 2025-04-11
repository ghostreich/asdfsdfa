import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components
from urllib.parse import urlparse, parse_qs

# ✅ 반드시 첫 번째 Streamlit 명령어
st.set_page_config(page_title="마인크래프트 건축물 기록", layout="centered")

# CSV 파일 경로 설정
CSV_FILE = "buildings.csv"

# CSV 파일이 없으면 생성
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["이름", "높이", "넓이", "건설 날짜", "만든 사람", "링크"])
        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

def load_data():
    return pd.read_csv(CSV_FILE, encoding="utf-8-sig")

def save_data(df):
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# URL 파라미터에서 모드 확인
query_params = st.query_params
mode = query_params.get("mode", ["edit"])[0]
readonly = mode == "view"

# 페이지 제목
st.title("🏗️ 마인크래프트 건축물 기록")
if readonly:
    st.info("🔒 현재는 보기 전용 모드입니다. 건축물을 추가하거나 삭제할 수 없습니다.")

# 데이터 초기화
initialize_csv()
df = load_data()

# 탭 설정
탭 = st.radio("메뉴 선택", ["건축물 목록 보기", "건축물 추가하기", "건축물 삭제하기"], horizontal=True)

# 정렬 기능 변수
df_sorted = df.copy()

# --- 목록 보기 탭 ---
if 탭 == "건축물 목록 보기":
    st.subheader("📋 건축물 목록")

    정렬기준 = st.selectbox("정렬 기준을 선택하세요", ["이름", "높이", "넓이", "건설 날짜", "만든 사람"], index=0)
    정렬방식 = st.radio("정렬 방식", ["오름차순", "내림차순"], horizontal=True)

    오름차순 = True if 정렬방식 == "오름차순" else False

    try:
        if 정렬기준 in ["높이", "넓이"]:
            df_sorted[정렬기준] = pd.to_numeric(df_sorted[정렬기준], errors='coerce')
        df_sorted = df_sorted.sort_values(by=정렬기준, ascending=오름차순)
    except:
        st.warning("정렬에 실패했습니다.")

    if "링크" in df_sorted.columns:
        df_sorted["링크"] = df_sorted["링크"].apply(lambda x: f"[열기]({x})" if pd.notnull(x) and str(x).strip() != "" else "")

    if df_sorted.empty:
        st.info("표시할 건축물이 없습니다.")
    else:
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)

# --- 추가하기 탭 ---
elif 탭 == "건축물 추가하기":
    st.subheader("➕ 건축물 추가")

    if readonly:
        st.warning("이 모드에서는 건축물을 추가할 수 없습니다.")
    else:
        이름 = st.text_input("건축물 이름")
        높이 = st.number_input("높이 (블록 수)", min_value=1)
        넓이 = st.number_input("넓이 (블록 수)", min_value=1)
        날짜 = st.date_input("건설된 날짜", value=datetime.today())
        만든사람 = st.text_input("만든 사람")
        링크 = st.text_input("관련 링크 (선택 사항)")

        저장버튼 = st.button("저장하기")

        if 저장버튼:
            if 이름 and 만든사람:
                새로운행 = pd.DataFrame([[이름, 높이, 넓이, 날짜.strftime('%Y-%m-%d'), 만든사람, 링크]],
                                       columns=["이름", "높이", "넓이", "건설 날짜", "만든 사람", "링크"])
                df = pd.concat([df, 새로운행], ignore_index=True)
                save_data(df)
                st.success("✅ 건축물이 저장되었습니다!")
            else:
                st.warning("⚠️ 이름과 만든 사람은 반드시 입력해야 합니다.")

# --- 삭제하기 탭 ---
elif 탭 == "건축물 삭제하기":
    st.subheader("❌ 건축물 삭제")

    if readonly:
        st.warning("이 모드에서는 건축물을 삭제할 수 없습니다.")
    else:
        이름검색 = st.text_input("삭제할 건축물 이름 검색")
        삭제후보 = df[df["이름"].str.contains(이름검색, na=False)] if 이름검색 else df

        선택 = st.selectbox("삭제할 건축물을 선택하세요", 삭제후보["이름"] if not 삭제후보.empty else ["없음"])

        if 선택 != "없음":
            if st.checkbox("정말 삭제하시겠습니까?"):
                if st.button("삭제하기"):
                    df = df[df["이름"] != 선택]
                    save_data(df)
                    st.success(f"🗑️ '{선택}' 건축물이 삭제되었습니다.")
