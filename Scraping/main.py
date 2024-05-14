# from utils import search_google_scholar, get_abstract, summarize_v2
from cinii import search_cinii, translate_en_to_ja
import streamlit as st
import const
from streamlit_option_menu import option_menu
st.set_page_config(**const.SET_PAGE_CONFIG)
st.markdown(const.HIDE_ST_STYLE, unsafe_allow_html=True)
# selected = option_menu(**const.OPTION_MENU_CONFIG)

from dotenv import load_dotenv
load_dotenv()

st.title("Scraping")
# カラムレイアウトを作成
# selected_model = st.sidebar.selectbox(
#     '使用するモデルを選択：',
#     ['gpt-35-turbo', 'gpt-4']
# )
orders = {'出版年：新しい順': 0, '被引用件数：多い順': 10, '関連度：高い順': 4}
sort_order = st.sidebar.selectbox(
    '並びかたを選択：',
    list(orders.keys())
)
period = st.sidebar.slider(
    '期間を選択', 2000, 2024, (2000, 2024), 1
)
query = st.text_input("キーワード")

# submit_button = st.button("検索", key="submit")
with st.spinner("処理中..."):
    if query:
        results = search_cinii(query, orders[sort_order], period=period, pagenum=1)
        # 検索結果を表示
        n=0
        for i in range(len(results["titles"])):
            st.markdown('### Title:')
            st.markdown(f"{results['titles'][i]} [リンク](https://cir.nii.ac.jp{results['links'][i]})")
            st.markdown('### info:')
            st.markdown(results['infos'][i])
            # if orders==10:
            #     st.markdown(results['quotes'][i])
            st.markdown('### abstracts:')
            st.markdown(results['abstracts'][i])
            if st.button("翻訳", key=f"abstract{n}"):
                st.markdown(translate_en_to_ja(results['abstracts'][i]))
            st.markdown('---')
            n+=1
    # else:
    #     st.write("入力されていません")