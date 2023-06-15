import os
import string

import requests
from bs4 import BeautifulSoup

number_of_articles = int(input())
type_of_articles = input()


def change_name(name):
    ans = ''
    if name[0] == '‘':
        name = name[1:]

    if name[-1] == '’':
        name = name[:len(name) - 1]

    for i in name:
        if i in string.punctuation:
            ans += ''
        elif i == ' ':
            ans += '_'
        elif i == '’':
            ans += '_'
        else:
            ans += i
    return ans


def get_max_pagination():
    url = 'https://www.nature.com/nature/articles?searchType=journalSearch&sort=PubDate&year=2020&page=1'
    page_content = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.5'}).content
    soup = BeautifulSoup(page_content, 'html.parser')
    navi = soup.find_all('li', class_='c-pagination__item')
    max_page_number = 0
    for nav in navi:
        value = nav.attrs.get('data-page', 'None')
        if value.isdigit():
            max_page_number = max(max_page_number, int(value))

    return max_page_number


max_pagination = get_max_pagination()


def pages_walker(max_pagination, number_of_articles, type_of_articles):
    save_article_counter = 0
    for page in range(1, max_pagination + 1):
        if not os.path.exists(f'Page_{page}'):
            os.mkdir(f'Page_{page}')

        if save_article_counter >= number_of_articles:
            break

        else:
            url = f'https://www.nature.com/nature/articles?searchType=journalSearch&sort=PubDate&year=2020&page={page}'
            page_content = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.5'}).content
            soup = BeautifulSoup(page_content, 'html.parser')
            articles = soup.find_all('article')

            for article in articles:
                if save_article_counter >= number_of_articles:
                    break
                else:
                    article_span = article.find('span', {'data-test': 'article.type'}).text
                    if article_span == type_of_articles:
                        article_link = article.find('a', href=True)['href']
                        article_view_link = 'https://www.nature.com' + article_link

                        req = requests.get(article_view_link, headers={'Accept-Language': 'en-US,en;q=0.5'}).content

                        soup_inside = BeautifulSoup(req, 'html.parser')
                        article_title = soup_inside.find('title').text
                        article_title = change_name(article_title)
                        article_description = soup_inside.find('p', class_='article__teaser')

                        if article_description == None:
                            article_description = soup_inside.find('meta', {'name': 'description'})['content']
                            print(article_description)
                        else:
                            article_description = article_description.text

                        file = open(f'Page_{page}/{article_title}.txt', 'w')
                        file.write(article_description)
                        file.close()

                        save_article_counter += 1

    print('Saved all articles.')


pages_walker(max_pagination, number_of_articles, type_of_articles)
