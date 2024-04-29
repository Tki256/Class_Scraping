import requests
from bs4 import BeautifulSoup
import re  

def search_google_scholar(query):
    # 検索クエリをGoogle Scholar用にエンコード
    encoded_query = requests.utils.quote(query)
    
    # Google Scholarの検索結果ページのURL
    url = f'https://scholar.google.com/scholar?q={encoded_query}'
    
    # HTMLを取得
    response = requests.get(url)
    html_content = response.text
    
    # BeautifulSoupでHTMLをパース
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 検索結果の各論文情報を抽出
    results = []
    for result in soup.find_all('div', class_='gs_r'):
        # タイトル
        title_element = result.find('h3', class_='gs_rt')
        title = title_element.get_text().strip() if title_element else ''
        
        # URL
        link_element = result.find_all('h3')
        for link in link_element:
          link = link.find('a') if link_element else ''
          if link:
            link = link['href']
            break
        
        # 著者
        author_element = result.find('div', class_='gs_a')
        authors = author_element.get_text().strip() if author_element else ''
        
        # a タグからhref属性を取得
        pdf_element = result.find('a')
        pdf = pdf_element['href'] if pdf_element else ''
        # PDFリンクが.pdfで終わらない場合、空文字列に置き換える
        if not pdf.endswith('.pdf'):
            pdf = ''
            
        # 要素取れなかったらスキップ
        if title == '' or link == '' or author_element == '' or pdf == '': continue
        
        # 結果をリストに追加
        results.append({
            'title': title,
            'authors': authors,
            'URL': link,
            'pdf': pdf
        })
    
    return results

def get_abstract(link):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    paper_response = requests.get(link, headers=headers)
    paper_html = paper_response.text
    soup = BeautifulSoup(paper_html, "html.parser")

    abstract = soup.find_all(class_=lambda x: x and 'abstract' in x)
  # abstract = soup.find_all(class_='abstract')
    if not abstract:
        return None
    
    abstract_text = ""
    for i in abstract:
        text = i.find('p')
        if text:
            abstract_text += text.get_text().strip()
    return abstract_text


# azure openai api
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings

def is_all_digits(text):
    return text.isdigit()

def get_pdf(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    file_name = url.split("/")[-1]
    if is_all_digits(file_name[:-4]):
        # file_name = f"paper-{file_name}"
        return None
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open('file.pdf', 'wb') as f:
            f.write(response.content)
        reader = PyPDFLoader('file.pdf')
        return reader
        # PDFの処理を続ける
    else:
        print(f'Failed to download PDF. Status code: {response.status_code}')
        return None

def summarize_v2(url, model="gpt-35-turbo"):
    # loader = PyPDFLoader(f"./Scraping/track_pdfs/{file_name}")
    loader = get_pdf(url)
    if loader is None:
        return None
    
    documents = loader.load()
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding",
        openai_api_version="2023-12-01-preview",
    )
    # テキストを分割
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(split_docs, embeddings)

    prompt_template = """
        #お願い
        あなたはプロの要約者です。各章を関連付けて、論文の内容を簡潔に要約してください。

        #ルール
        日本語での出力

        #入力
        {text}
        
        #出力
        タイトル
        著者名
        雑誌名
        公開年月日
        論文の主要なポイント
        論文の重要性"""
        
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    # OpenAI APIを使用して要約チェーンを作成
    llm = AzureChatOpenAI(
        openai_api_version="2023-12-01-preview",
        azure_deployment="gpt-35-turbo",
    )
    chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=PROMPT)
    # ベクターストアからドキュメントを取得
    # docs = db.similarity_search(query="abstruct", k=2)
    retriver = db.as_retriever(search_kwargs={"k": 4})
    docs = retriver.get_relevant_documents("abstruct")
    combined_doc = combine_documents(docs)
    # ドキュメントの要約を生成
    summary = chain.run(combined_doc)

    return summary



# シンプル
from langchain.docstore.document import Document

def combine_documents(docs):
    text = "\n\n".join([doc.page_content for doc in docs])
    metadata = {"source": "combined"}
    return Document(page_content=text, metadata=metadata)




