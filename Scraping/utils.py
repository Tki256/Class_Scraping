import requests
import bs4 import BeautifulSoup
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
          link = link.find('a')
          if link:
            link = link['href']
            break
        # print(link_element)
        # link = link_element['href'] if link_element else ''
        
        # 著者
        author_element = result.find('div', class_='gs_a')
        authors = author_element.get_text().strip() if author_element else ''
        
        
        # 結果をリストに追加
        results.append({
            'title': title,
            'authors': authors,
            'URL': link
        })
    
    return results

def get_abstract(link):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
  }
  paper_response = requests.get(links[0], headers=headers)
  paper_html = paper_response.text
  soup = BeautifulSoup(paper_html, "html.parser")

  abstract = soup.find_all(class_=lambda x: x and 'abstract' in x)
  if not abstract:
    return None
    
  abstract_text = ""
  for i in abstract:
    abstract_text += i.text
  return abstract_text