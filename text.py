import requests
from bs4 import BeautifulSoup
import pandas as pd
df = pd.DataFrame([[article.get_text(), section.get('aria-label'), article.find_parent('section').find('span', {'class': 'author'}).get_text() if article.find_parent('section').find('span', {'class': 'author'}) else 'N/A', article.find_parent('time').get('datetime') if article.find_parent('time') else 'N/A', article.find_parent('a')['href'] if article.find_parent('a') else 'N/A'] for section in BeautifulSoup(requests.get('https://www.usatoday.com/').text, 'html.parser').find_all('section', {'aria-label': ['Entertainment', 'Sports', 'Life']}) for article in section.find_all('h3')], columns=['Title', 'Category', 'Author', 'Publishing Date', 'URL']); print(df)
print(df)

url = 'https://usatoday.com' 
response= BeautifulSoup(requests.get(url).text)
print(response)