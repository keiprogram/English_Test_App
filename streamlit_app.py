import streamlit as st
import pandas as pd
import random

# 背景色と文字色の設定
page_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #5d79ba;
    color: #9c944f;
}
[data-testid="stSidebar"] {
    background-color: #9c944f;
    color: #5d79ba;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# Excelファイルの読み込み
try:
    excel_file = "シスタン.xlsx"
    sheet_name = "Sheet1"
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
except FileNotFoundError:
    st.error("エクセルファイルが見つかりません。ファイル名と場所を確認してください。")
    st.stop()

# データフレームのカラムを取得
english_words = df['English'].tolist()
japanese_meanings = df['Japanese'].tolist()

# 問題数を設定
num_questions = 10

# テストの実施
st.title("英単語テストアプリ")

# セッションステートの初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.correct_answers = 0
    st.session_state.questions = random.sample(range(len(english_words)), num_questions)

# 現在の質問を取得
current_index = st.session_state.questions[st.session_state.current_question]
current_english = english_words[current_index]
current_japanese = japanese_meanings[current_index]

# 問題の表示
st.header(f"問題 {st.session_state.current_question + 1} / {num_questions}")
st.write(f"次の英単語の意味を選んでください: **{current_english}**")

# 選択肢の生成
options = random.sample(japanese_meanings, 3)
if current_japanese not in options:
    options[random.randint(0, 2)] = current_japanese
random.shuffle(options)

# ユーザーの回答
user_answer = st.radio("選択肢", options, index=-1)

if st.button("回答を提出"):
    if user_answer == current_japanese:
        st.success("正解です！")
        st.session_state.correct_answers += 1
    else:
        st.error(f"不正解です。正しい答え: {current_japanese}")

    # 次の質問へ
    st.session_state.current_question += 1

    # 全ての問題が終了したか確認
    if st.session_state.current_question >= num_questions:
        st.success(f"テスト終了！正解数: {st.session_state.correct_answers} / {num_questions}")
        st.balloons()
        st.session_state.current_question = 0
        st.session_state.correct_answers = 0
        st.session_state.questions = random.sample(range(len(english_words)), num_questions)
