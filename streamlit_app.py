import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="英単語テスト")

# CSS for custom background
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f4efd1 80%, #df3b1f 20%);
        height: 100vh;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# タイトルと説明
st.title('英単語テスト')
st.write('英単語を順に表示して、勉強をサポートします！')

# Load the data from multiple Excel files
@st.cache_data
def load_data():
    part1 = pd.read_excel("リープベーシック見出語・用例リスト(Part 1).xlsx")
    part2 = pd.read_excel("リープベーシック見出語・用例リスト(Part 2).xlsx")
    part3 = pd.read_excel("リープベーシック見出語・用例リスト(Part 3).xlsx")
    part4 = pd.read_excel("リープベーシック見出語・用例リスト(Part 4).xlsx")
    return pd.concat([part1, part2, part3, part4], ignore_index=True)

words_df = load_data()

# Define the range options for the test
total_words = len(words_df)
range_options = [(i, min(i+99, total_words-1)) for i in range(0, total_words, 100)]

# Select the range for the test
selected_range = st.selectbox('出題範囲を選択してください:', range_options, format_func=lambda x: f"{x[0]+1}-{x[1]+1}")

# Filter words based on the selected range
filtered_words_df = words_df.iloc[selected_range[0]:selected_range[1]+1]

# Select a random sample of 50 words for the test
test_words_df = filtered_words_df.sample(n=50, random_state=1).reset_index(drop=True)

# Variables to track the test state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'incorrect_words' not in st.session_state:
    st.session_state.incorrect_words = []

# Function to evaluate the answer and update the score
def evaluate_answer(index, answer, correct_option):
    if answer == correct_option:
        st.session_state.score += 1
    else:
        st.session_state.incorrect_words.append((test_words_df.iloc[index]['単語'], correct_option))
    st.session_state.current_index += 1
    st.experimental_rerun()

# Function to present the current word and options
def present_question(index):
    word = test_words_df.iloc[index]['単語']
    options = test_words_df.sample(n=4)['語の意味'].tolist()
    correct_option = test_words_df.iloc[index]['語の意味']
    if correct_option not in options:
        options[np.random.randint(0, 4)] = correct_option
    st.write(f"問題 {index + 1}: {word} の意味は？")
    answer = st.radio("選択肢", options, key=f"question_{index}", on_change=evaluate_answer, args=(index, answer, correct_option))

# Main test loop
if st.session_state.current_index < len(test_words_df):
    present_question(st.session_state.current_index)
else:
    st.write(f"テスト終了！ スコア: {st.session_state.score}/50")
    if st.session_state.incorrect_words:
        st.write("間違えた単語:")
        for word, correct_option in st.session_state.incorrect_words:
            st.write(f"{word}: {correct_option}")
