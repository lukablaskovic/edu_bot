import requests
from bs4 import BeautifulSoup

url_unipu = 'https://www.unipu.hr/novosti'
url_fipu = 'https://fipu.unipu.hr/fipu/novosti/'

response = requests.get(url_fipu, verify=False)
response.raise_for_status() 

soup = BeautifulSoup(response.text, 'html.parser')

news_container = soup.select('div.scrollable_content div.container div.row div.col-lg-9 div#area_middle div#cms_area_middle div.cms_module.portlet_news div.cms_module_html div.news.Default_news_layout.news_layout_type_default')

articles = []

for article in news_container:
    news_articles = article.find_all('div', class_='news_article card news_priority_5 image_left')
    for news in news_articles:
        title = news.find('div', class_='news_title_truncateable').text.strip()
        link = news.find('a')['href']
        pub_date = news.find('div', class_='news_pub_date').find('time')['datetime']
        author = news.find('div', class_='author_name').text.strip() if news.find('div', class_='author_name') else 'N/A'
        image = news.find('img', class_='news_lead_image')['src'] if news.find('img', class_='news_lead_image') else 'N/A'
        summary = news.find('div', class_='news_lead_small').text.strip()

        articles.append({
            'title': title,
            'link': link,
            'pub_date': pub_date,
            'author': author,
            'image': image,
            'summary': summary
        })

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Publication Date: {article['pub_date']}")
    print(f"Author: {article['author']}")
    print(f"Image: {article['image']}")
    print(f"Summary: {article['summary']}")
    print('-' * 80)
