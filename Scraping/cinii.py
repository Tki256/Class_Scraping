import requests
from bs4 import BeautifulSoup
import re
import deepl
import os

def search_cinii(query, sortorder=0, period=None, pagenum=1):
    encoded_query = requests.utils.quote(query)
    
    # ciniiの検索結果ページのURL
    url = f'https://cir.nii.ac.jp/articles?q={encoded_query}&hasLinkToFullText=true&sortorder={sortorder}'
    if pagenum != 1:
        url += f'&page={pagenum}'
    if period:
        url += f'&from={period[0]}&until={period[1]}'
    # HTMLを取得
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoupでHTMLをパース
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all('div', class_='listitem')
    titles = []
    links = []
    infos = []
    # quotes = []
    for element in elements:
        links.append(element.find('a', class_='taggedlink')['href'])
        titles.append(element.find('a', class_='taggedlink').get_text())
        infos.append(element.find('p', class_='item_data').get_text(strip=True) \
        .replace('\n', '').replace('\t', '').replace('                           ', ''))
        # if sortorder == 10:
        #     quotes.append(element.find('span', class_='tag-cited').get_text(strip=True))
    abstracts = []
    for link in links:
        abstracts.append(get_abstract(link))
    
    results = {
        'titles': titles,
        'links': links,
        'infos': infos,
        'abstracts': abstracts,
        # 'quotes': quotes
    }
    return results

def get_abstract(link):
    url = "https://cir.nii.ac.jp" + link
    # HTMLを取得
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoupでHTMLをパース
    soup = BeautifulSoup(html_content, 'html.parser')
    abstract_element = soup.find('div', class_='metadataLists abstract')
    if abstract_element:
        abstract = abstract_element.get_text(strip=True)
        abstract = abstract.replace('application/pdf', '').replace('<p>', '').replace('</p>', '')
    else:
        abstract = "要約が見つかりませんでした。自分で読んでね！"
    return abstract

def translate_en_to_ja(text, auth_key=None):
    if auth_key != None:
        translator = deepl.Translator(auth_key=auth_key)
    else:
        translator = deepl.Translator(auth_key=os.getenv('DEEPL_API_KEY'))
    result = translator.translate_text(text, target_lang="JA")
    return result.text