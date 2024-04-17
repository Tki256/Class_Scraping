from utils import search_google_scholar, get_abstract

search_results = search_google_scholar("EEG stress")

# 検索結果を表示
for result in search_results:
    print('Title:', result['title'])
    print('Authors:', result['authors'])
    print('URL:', result['URL'])
    print('---')