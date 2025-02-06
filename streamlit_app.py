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
    try:
        data = pd.read_excel("シスタン.xlsx")
        data.columns = data.columns.str.strip()  # 列名の空白を削除
        return data
    except Exception as e:
        st.error(f"Excelファイルの読み込みに失敗しました: {e}")
        return None

# サイドバーでテスト形式を選択する
st.sidebar.title('単語帳を選択してください')
test_type = st.sidebar.radio("テスト形式", ('英語→日本語', '日本語→英語'), horizontal=True)

st.sidebar.title('出題範囲を選択してください')
ranges = [f"{i*100+1}-{(i+1)*100}" for i in range(14)]
selected_range = st.sidebar.selectbox("出題範囲", ranges)

# サイドバーで出題数を選択するスライダーを追加
st.sidebar.title('出題数を選択してください')
num_questions = st.sidebar.slider('出題数', min_value=1, max_value=50, value=10)

# シスタン.xlsxから単語データを読み込む
words_df = load_data()
if words_df is not None:
    # 必要な列が存在するか確認
    required_columns = ['No.']
    if not all(col in words_df.columns for col in required_columns):
        st.error("データフレームに必要な列が見つかりません。Excelファイルの列名を確認してください。")
        st.write(f"検出された列名: {words_df.columns.tolist()}")
    else:
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
