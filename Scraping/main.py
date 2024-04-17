from utils import search_google_scholar, get_abstract
import streamlit as st


st.title("Scraping")
# カラムレイアウトを作成

query = st.text_input("キーワード")

submit_button = st.button("検索", key="submit")
    
if submit_button:
    search_results = search_google_scholar(query)

    # 検索結果を表示
    n=1
    for result in search_results:
        st.markdown('### Title:')
        st.text(result['title'])
        st.markdown('### Authors:')
        st.text(result['authors'])
        st.markdown('### URL:')
        st.text(result['URL'])
        # if st.button("要約", key=f"abstract{n}"):
        #     st.text(get_abstract(result['URL']))
        st.markdown('### 要約:')
        st.text(get_abstract(result['URL']))
        st.markdown('---')
        n += 1
# else:
#     st.write("入力されていません")