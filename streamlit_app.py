import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import base64

st.set_page_config(page_title="English Vocabulary Test", page_icon='img/English_fabikon.png')

st.markdown(
    """ 
    <style>
    .reportview-container, .sidebar .sidebar-content {
        background-color: #022033;
        color: #ffae4b;
    }
    .stButton > button, .choice-button {
        background-color: #ffae4b;
        color: #022033;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton > button:hover, .choice-button:hover {
        background-color: #ffd17f;
    }
    .choices-container, .header-container, .button-container, .results-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
    }
    .results-table {
        border-collapse: collapse;
        width: 100%;
    }
    .results-table th, .results-table td {
        border: 1px solid #ffae4b;
        padding: 8px;
        text-align: center;
    }
    .results-table th {
        background-color: #022033;
        color: #ffae4b;
    }
    .results-table tr:nth-child(even) {
        background-color: #e3e3e3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def load_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_path = 'img/English.png'
image_base64 = load_image(image_path)
image_html = f'<img src="data:image/png;base64,{image_base64}" style="border-radius: 20px; width: 500px;">'

st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown(image_html, unsafe_allow_html=True)
st.title('英単語テスト')
st.write('英単語を順に表示して、勉強をサポートします！')
st.markdown('</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    # シスタン.xlsxファイルからデータを読み込む
    return pd.read_excel("シスタン.xlsx")

# サイドバーでテスト形式を選択する
st.sidebar.title('単語帳を選択してください')
test_type = st.sidebar.radio("テスト形式", ('英語→日本語', '日本語→英語'), horizontal=True)

st.sidebar.title('出題範囲を選択してください')
ranges = [f"{i*100+1}-{(i+1)*100}" for i in range(14)]
selected_range = st.sidebar.selectbox("出題範囲", ranges)

# サイドバーで出題数を選択するスライダーを追加
st.sidebar.title('出題数を選択してください')
num_questions = st.sidebar.slider('出題数', min_value=1, max_value=50, value=10)
<<<<<<< HEAD

# シスタン.xlsxから単語データを読み込む
words_df = load_data()
=======
>>>>>>> 67e28c2 (あｓ)

range_start, range_end = map(int, selected_range.split('-'))
filtered_words_df = words_df[(words_df['No.'] >= range_start) & (words_df['No.'] <= range_end)].sort_values(by='No.')

if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
    })

    # 選択した出題数に基づいてランダムに問題を選択
    selected_questions = filtered_words_df.sample(num_questions).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    if test_type == '英語→日本語':
        options = list(selected_questions['語の意味'].sample(3))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(selected_questions['単語'].sample(3))
        options.append(st.session_state.current_question_data['単語'])
    
    np.random.shuffle(options)
    st.session_state.options = options
    st.session_state.answer = None

def update_question(answer):
    if test_type == '英語→日本語':
        correct_answer = st.session_state.current_question_data['語の意味']
        question_word = st.session_state.current_question_data['単語']
    else:
        correct_answer = st.session_state.current_question_data['単語']
        question_word = st.session_state.current_question_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append((
            st.session_state.current_question_data['No.'],
            question_word,
            correct_answer
        ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        if test_type == '英語→日本語':
            options = list(st.session_state.selected_questions['語の意味'].sample(3))
            options.append(st.session_state.current_question_data['語の意味'])
        else:
            options = list(st.session_state.selected_questions['単語'].sample(3))
            options.append(st.session_state.current_question_data['単語'])
        np.random.shuffle(options)
        st.session_state.options = options
        st.session_state.answer = None
    else:
        st.session_state.finished = True

def display_results():
    correct_answers = st.session_state.correct_answers
    total_questions = st.session_state.total_questions
    wrong_answers = [wa for wa in st.session_state.wrong_answers if wa[0] in st.session_state.selected_questions['No.'].values]
    accuracy = correct_answers / total_questions

    st.write(f"テスト終了！正解数: {correct_answers}/{total_questions}")
    st.progress(accuracy)
    
    st.write("正解数と不正解数")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("正解数", correct_answers)
    with col2:
        st.metric("不正解数", total_questions - correct_answers)

    st.write(f"正答率: {accuracy:.0%}")
    st.progress(accuracy)
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    if wrong_answers:
        df_wrong_answers = pd.DataFrame(wrong_answers, columns=["問題番号", "単語", "語の意味"])
        df_wrong_answers = df_wrong_answers.sort_values(by="問題番号")
        st.markdown(df_wrong_answers.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.write("間違えた問題はありません。")
    st.markdown('</div>', unsafe_allow_html=True)

if 'test_started' in st.session_state and not st.session_state.finished:
    st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions}")
    st.subheader(f"{st.session_state.current_question_data['単語']}" if test_type == '英語→日本語' else f"{st.session_state.current_question_data['語の意味']}")
    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(st.session_state.options):
        st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if 'test_started' in st.session_state and st.session_state.finished:
        display_results()
