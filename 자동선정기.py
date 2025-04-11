import streamlit as st
import pandas as pd
import numpy as np
import io

# 연령 조건 함수
def is_eligible(acode, age):
    유아코드 = ['A01', 'A02', 'A26']
    저학년코드 = ['A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11', 'A12', 'A13', 'A14',
                 'A22', 'A23', 'A24', 'A25', 'A27', 'A28', 'A31', 'A32', 'A33', 'A34', 'A35']
    고학년코드 = ['A06', 'A07', 'A08', 'A09', 'A10', 'A11', 'A12', 'A13', 'A14',
                 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A22', 'A23', 'A24', 'A25',
                 'A29', 'A30', 'A31', 'A32', 'A33', 'A34', 'A35']
    
    if acode in 유아코드:
        return age in [6, 7]
    elif acode in 저학년코드:
        return age in [8, 9, 10]
    elif acode in 고학년코드:
        return age in [11, 12, 13]
    else:
        return False

def extract_age(value):
    import re
    match = re.search(r'(\d+)세', str(value))
    return int(match.group(1)) if match else None

st.title("🎲 교육 프로그램 무작위 선정기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드해주세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['나이'] = df['학년'].apply(extract_age)
    df['연령허용'] = df.apply(lambda row: is_eligible(row['A코드'], row['나이']), axis=1)
    df['과목코드'] = df['A코드'] + '-' + df['B코드']

    valid_df = df[df['연령허용']].copy()
    selected_final = pd.DataFrame()
    used_names = set()

    for subject_code, group in valid_df.groupby('과목코드'):
        group = group[~group['참가자'].isin(used_names)]
        if len(group) >= 20:
            selected_count = np.random.randint(20, min(28, len(group) + 1))
            selected_group = group.sample(n=selected_count, random_state=42)
        else:
            selected_group = group
        used_names.update(selected_group['참가자'].tolist())
        selected_final = pd.concat([selected_final, selected_group], ignore_index=True)

    df['선정'] = '미선정'
    for idx, row in selected_final.iterrows():
        mask = (
            (df['참가자'] == row['참가자']) &
            (df['A코드'] == row['A코드']) &
            (df['B코드'] == row['B코드'])
        )
        df.loc[mask, '선정'] = '선정'

    st.success("🎉 추첨이 완료되었습니다!")
    st.dataframe(df[['참가자', 'A코드', 'B코드', '나이', '선정']])

    # 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label="📥 선정결과 엑셀 다운로드",
        data=output.getvalue(),
        file_name="최종_선정결과_전체명단.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
