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

# セッション状態の初期化
if 'wrong_answers' not in st.session_state:
    st.session_state.wrong_answers = []
if 'test_started' not in st.session_state:
    st.session_state.test_started = False

# UI設定
st.title("English Vocabulary Test")
st.caption("アップロードされた単語帳で学ぶ英単語テストアプリ")

# テスト形式選択
test_mode = st.sidebar.radio("テスト形式を選択", ["英語→日本語", "日本語→英語", "間違えた問題"])

# 範囲指定 (No.1〜No.100形式)
max_no = int(words_df["No."].max())
ranges = [(i, min(i+99, max_no)) for i in range(1, max_no+1, 100)]
range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
selected_label = st.sidebar.selectbox("出題範囲", range_labels)
selected_range = ranges[range_labels.index(selected_label)]

# 出題数選択
num_questions = st.sidebar.slider("出題数", 1, 50, 10)

# データ抽出
if test_mode == "間違えた問題" and st.session_state.wrong_answers:
    filtered_df = pd.DataFrame(st.session_state.wrong_answers, columns=["No.", "単語", "語の意味"])
else:
    filtered_df = words_df[(words_df["No."] >= selected_range[0]) & (words_df["No."] <= selected_range[1])]

# テスト開始ボタンをメイン画面に配置
if st.button("テスト開始"):
    if test_mode == "間違えた問題" and not st.session_state.wrong_answers:
        st.warning("まだ間違えた問題がありません。通常のテストを行ってください。")
    else:
        st.session_state.test_started = True
        st.session_state.questions = filtered_df.sample(n=min(num_questions, len(filtered_df))).reset_index(drop=True)
        st.session_state.current = 0
        st.session_state.correct = 0
        st.session_state.temp_wrongs = []

# 回答処理関数
def answer_question(opt):
    q = st.session_state.questions.iloc[st.session_state.current]
    correct = q["語の意味"] if test_mode in ["英語→日本語", "間違えた問題"] else q["単語"]
    if opt == correct:
        st.session_state.correct += 1
        # 正解した場合、間違えた問題リストから削除
        if test_mode == "間違えた問題":
            wrong_list = st.session_state.wrong_answers
            st.session_state.wrong_answers = [w for w in wrong_list if w[0] != q["No."]]
    else:
        # "わからない"を選択した場合も間違えた問題として記録
        st.session_state.temp_wrongs.append((q["No."], q["単語"], q["語の意味"]))
    st.session_state.current += 1

# テスト進行
if st.session_state.get("test_started", False) and st.session_state.current < len(st.session_state.questions):
    q = st.session_state.questions.iloc[st.session_state.current]
    question_text = q["単語"] if test_mode in ["英語→日本語", "間違えた問題"] else q["語の意味"]
    correct_answer = q["語の意味"] if test_mode in ["英語→日本語", "間違えた問題"] else q["単語"]
    # 選択肢生成
    pool = filtered_df["語の意味"] if test_mode in ["英語→日本語", "間違えた問題"] else filtered_df["単語"]
    # 正解を除いたプールからランダムに4つの誤答を選択
    choices = list(pool[pool != correct_answer].drop_duplicates().sample(n=min(4, len(pool[pool != correct_answer].drop_duplicates()))))
    # 正解が選択肢に含まれていない場合、正解を追加
    if correct_answer not in choices:
        choices.append(correct_answer)
    # 選択肢が4つ未満の場合、ダミー選択肢を追加
    while len(choices) < 4:
        choices.append(f"ダミー選択肢 {len(choices)+1}")
    # 「わからない」を追加
    choices.append("わからない")
    np.random.shuffle(choices)

    st.subheader(f"問題 {st.session_state.current+1} / {len(st.session_state.questions)}")
    # 進捗バーの追加
    st.progress((st.session_state.current) / len(st.session_state.questions))
    st.write(question_text)

    for opt in choices:
        st.button(opt, on_click=answer_question, args=(opt,))

# 結果表示
elif st.session_state.get("test_started", False) and st.session_state.current >= len(st.session_state.questions):
    total = len(st.session_state.questionsimport streamlit as st
import pandas as pd
import numpy as np
import random

# データの読み込み
uploaded_file = "/mnt/data/pass1.xlsx"
df = pd.read_excel(uploaded_file)

# グループ番号の範囲でフィルタリングする関数
def get_range_options():
    max_group = df["Group No."].max()
    ranges = [(i, min(i + 99, max_group)) for i in range(1, max_group + 1, 100)]
    return [f"No.{start}~No.{end}" for start, end in ranges]

def filter_df_by_range(selected_range):
    start, end = map(int, selected_range.replace("No.", "").split("~"))
    return df[(df["Group No."] >= start) & (df["Group No."] <= end)]

# 初期化
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "options" not in st.session_state:
    st.session_state.options = []
if "current_question_data" not in st.session_state:
    st.session_state.current_question_data = {}

# アプリのタイトル
st.title("English Vocabulary TEST App")

# 単語範囲選択
selected_range = st.selectbox("出題範囲を選んでください", get_range_options())
filtered_words_df = filter_df_by_range(selected_range)

# 出題モード選択
test_type = st.radio("出題形式を選んでください", ["英語→日本語", "日本語→英語"])

# 問題数の指定
num_questions = st.slider("出題数を選んでください", min_value=1, max_value=20, value=5)

# 問題のシャッフルと生成
def generate_questions():
    sampled = filtered_words_df.sample(n=num_questions).reset_index(drop=True)
    st.session_state.questions = sampled.to_dict(orient="records")
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.current_question_data = st.session_state.questions[0]
    generate_options()

# 選択肢の生成
def generate_options():
    current = st.session_state.current_question_data
    correct = current["語の意味"] if test_type == "英語→日本語" else current["単語"]
    col = "語の意味" if test_type == "英語→日本語" else "単語"
    dummy_df = filtered_words_df[filtered_words_df[col] != correct]
    dummy_options = dummy_df[col].sample(min(3, len(dummy_df))).tolist()
    options = dummy_options + [correct]
    random.shuffle(options)
    st.session_state.options = options

# 回答チェックと次の問題へ
def check_answer(selected_option):
    current = st.session_state.current_question_data
    correct = current["語の意味"] if test_type == "英語→日本語" else current["単語"]
    if selected_option == correct:
        st.session_state.score += 1
        st.success("正解！")
    else:
        st.error(f"不正解。正解は {correct} です。")
    st.session_state.question_index += 1
    if st.session_state.question_index < len(st.session_state.questions):
        st.session_state.current_question_data = st.session_state.questions[st.session_state.question_index]
        generate_options()
    else:
        st.balloons()

# テスト開始
if st.button("テスト開始"):
    generate_questions()

# テスト実行中の画面
if st.session_state.questions and st.session_state.question_index < len(st.session_state.questions):
    current = st.session_state.current_question_data
    question_text = current["単語"] if test_type == "英語→日本語" else current["語の意味"]
    st.markdown(f"### Q{st.session_state.question_index + 1}: {question_text}")
    for option in st.session_state.options:
        if st.button(option, key=option):
            check_answer(option)
            st.experimental_rerun()

# 結果表示
if st.session_state.question_index >= len(st.session_state.questions) and st.session_state.questions:
    st.markdown(f"## テスト終了！あなたのスコア: {st.session_state.score} / {num_questions}")
)
    correct = st.session_state.correct
    # 間違えた問題を永続的に保存
    for wrong in st.session_state.temp_wrongs:
        if wrong not in st.session_state.wrong_answers:
            st.session_state.wrong_answers.append(wrong)
    
    st.success(f"テスト終了！ 正解数: {correct}/{total}")
    st.progress(correct/total)
    if st.session_state.temp_wrongs:
        df_wrong = pd.DataFrame(st.session_state.temp_wrongs, columns=["No.", "単語", "語の意味"])
        st.subheader("間違えた問題一覧")
        st.dataframe(df_wrong)
    else:
        st.write("全問正解です！おめでとうございます！")
    st.session_state.test_started = False