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
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = []
if 'test_started' not in st.session_state:
    st.session_state.test_started = False

# UI設定
image_path = os.path.join("img", "pasutann.png")
if os.path.exists(image_path):
    st.image(image_path)
else:
    st.warning("画像ファイルが見つかりません: " + image_path)
st.title("準一パス単English Vocabulary Test")
st.caption("英単語テストアプリ")

# テスト形式選択
test_mode = st.sidebar.radio("テスト形式を選択", ["英語→日本語", "日本語→英語", "間違えた問題"])

# 範囲指定 (No.1〜No.100形式)
max_no = int(words_df["No."].max())
ranges = [(i, min(i+99, max_no)) for i in range(1, max_no+1, 100)]
range_labels = [f"No.{start}〜No.{end}" for start, end in ranges]
selected_label = st.sidebar.selectbox("出題範囲", range_labels)
selected_range = ranges[range_labels.index(selected_label)]

# 出題数選択
num_questions = st.sidebar.slider("出題数", 1, 100, 50)

# データ抽出
if test_mode == "間違えた問題" and st.session_state.wrong_answers:
    filtered_df = pd.DataFrame(st.session_state.wrong_answers, columns=["No.", "単語", "語の意味"])
else:
    filtered_df = words_df[(words_df["No."] >= selected_range[0]) & (words_df["No."] <= selected_range[1])]

# テスト開始ボタンをメイン画面に配置
if st.button("テスト開始"):
    if test_mode == "間違えた問題" and not st.session_state.wrong_answers:
        st.warning("まだ間違えた問題がありません。通常のテストを行ってください。")
    elif len(filtered_df) == 0:
        st.error("選択した範囲に単語がありません。別の範囲を選択してください。")
    elif len(filtered_df) < num_questions:
        st.warning(f"選択した範囲の単語数（{len(filtered_df)}語）が指定した出題数（{num_questions}問）より少ないため、{len(filtered_df)}問でテストを開始します。")
        st.session_state.test_started = True
        st.session_state.questions = filtered_df.sample(n=len(filtered_df)).reset_index(drop=True)
        st.session_state.current = 0
        st.session_state.correct = 0
        st.session_state.temp_wrongs = []
    else:
        st.session_state.test_started = True
        st.session_state.questions = filtered_df.sample(n=num_questions).reset_index(drop=True)
        st.session_state.current = 0
        st.session_state.correct = 0
        st.session_state.temp_wrongs = []

# 回答処理関数
def answer_question(opt):
    if st.session_state.current >= len(st.session_state.questions):
        return  # Prevent index out of bounds
    q = st.session_state.questions.iloc[st.session_state.current]
    correct = q["語の意味"] if test_mode in ["英語→日本語", "間違えた問題"] else q["単語"]
    if opt == correct:
        st.session_state.correct += 1
        # 正解した場合、正解リストに追加
        st.session_state.correct_answers.append((q["No."], q["単語"], q["語の意味"]))
        # 間違えた問題リストから削除
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
    # 正解を除いたプールからランダムに最大4つの誤答を選択
    choices = list(pool[pool != correct_answer].drop_duplicates().sample(n=min(4, len(pool[pool != correct_answer].drop_duplicates()))))
    # 正解が選択肢に含まれていない場合、正解を追加
    if correct_answer not in choices:
        choices.append(correct_answer)
    # 選択肢が4つ未満の場合、範囲内のデータから補充
    if len(choices) < 4:
        # 既存の選択肢を除外したプールを用意
        remaining_pool = pool[~pool.isin(choices)].drop_duplicates()
        if len(remaining_pool) > 0:
            additional_choices = list(remaining_pool.sample(n=min(4 - len(choices), len(remaining_pool))))
            choices.extend(additional_choices)
        # それでも足りない場合、正解済みの問題から補充
        if len(choices) < 4 and st.session_state.correct_answers:
            correct_df = pd.DataFrame(st.session_state.correct_answers, columns=["No.", "単語", "語の意味"])
            correct_pool = correct_df["語の意味"] if test_mode in ["英語→日本語", "間違えた問題"] else correct_df["単語"]
            remaining_correct_pool = correct_pool[~correct_pool.isin(choices)].drop_duplicates()
            if len(remaining_correct_pool) > 0:
                additional_choices = list(remaining_correct_pool.sample(n=min(4 - len(choices), len(remaining_correct_pool))))
                choices.extend(additional_choices)
        # それでも足りない場合は警告を表示
        if len(choices) < 4:
            st.warning("選択肢が不足しています。範囲内の単語数および正解済みの問題が少ないため、選択肢を4つに満たせませんでした。")
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
    total = len(st.session_state.questions)
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