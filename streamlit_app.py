import streamlit as st
import pandas as pd
import numpy as np

# アプリ設定
st.set_page_config(page_title="English Vocabulary Test", page_icon="📝")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_excel("pass1.xlsx")
    df.columns = ["No.", "単語", "語の意味"]
    return df

words_df = load_data()

# UI設定
st.title("English Vocabulary Test")
st.caption("アップロードされた単語庫を使った英単語学習アプリ")

# テスト形式選択
test_type = st.sidebar.radio("Q1. テスト形式を選んでください", ["英語→日本語", "日本語→英語"])

# 範囲指定
max_no = words_df["No."].max()
ranges = [(i, i+99) for i in range(1, max_no+1, 100)]
range_labels = [f"No.{start}~No.{end}" for start, end in ranges]
selected_range_label = st.sidebar.selectbox("Q2. 出題範囲を選択", range_labels)
selected_range = ranges[range_labels.index(selected_range_label)]

# 問題数
num_questions = st.sidebar.slider("Q3. 出題数", 1, 50, 10)

# データ抽出
filtered_df = words_df[(words_df["No."] >= selected_range[0]) & (words_df["No."] <= selected_range[1])]

# テスト開始
if st.button("テスト開始"):
    st.session_state.test_started = True
    st.session_state.questions = filtered_df.sample(n=min(num_questions, len(filtered_df))).reset_index(drop=True)
    st.session_state.current = 0
    st.session_state.correct = 0
    st.session_state.wrongs = []

# テスト中
if st.session_state.get("test_started", False) and st.session_state.current < len(st.session_state.questions):
    q = st.session_state.questions.iloc[st.session_state.current]
    question_text = q["単語"] if test_type == "英語→日本語" else q["語の意味"]
    correct_answer = q["語の意味"] if test_type == "英語→日本語" else q["単語"]
    
    all_choices = filtered_df["語の意味"] if test_type == "英語→日本語" else filtered_df["単語"]
    options = list(all_choices.sample(3)) + [correct_answer]
    np.random.shuffle(options)

    st.subheader(f"Q{st.session_state.current+1}: {question_text}")
    for opt in options:
        if st.button(opt):
            if opt == correct_answer:
                st.session_state.correct += 1
            else:
                st.session_state.wrongs.append((q["No."], q["単語"], q["語の意味"]))
            st.session_state.current += 1
            st.experimental_rerun()

# 結果表示
if st.session_state.get("test_started", False) and st.session_state.current >= len(st.session_state.questions):
    total = len(st.session_state.questions)
    correct = st.session_state.correct
    st.success(f"テスト終了！ 正解数: {correct} / {total}")
    st.progress(correct / total)

    if st.session_state.wrongs:
        st.write("間違えた問題一覧")
        df_wrong = pd.DataFrame(st.session_state.wrongs, columns=["No.", "単語", "語の意味"])
        st.dataframe(df_wrong)
    else:
        st.write("全問正解です！すばらしい！")