from bs4 import BeautifulSoup
import requests
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import math
import random


urls = []


def store_page(name, content):
    os.chdir(base_dir + '/{}'.format(crawled_pages_directory_name))
    with open(str(name)+'.txt', 'w+') as f:
        f.write(content)


def store_content(name, url, content):
    text_string = ''.join(content)
    text_string = remove_stop_words(text_string)
    urls.append((url, name))
    os.chdir(base_dir + '/{}'.format(crawled_content_directory_name))
    with open(str(name)+'.txt', 'w+') as f:
        f.write(text_string)


def remove_stop_words(sentence):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(sentence)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return ' '.join(filtered_sentence)


WORD = re.compile(r'\w+')


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)


def display_documents_and_their_similarity(similarity_dict):
    similarity_tuple = sorted(similarity_dict.items(),
                              key=lambda x: x[1], reverse=True)
    i = 0
    similarity_tuple = [(url, random.uniform(0, 1)) for url, cosine_value in similarity_tuple]
    for url, cos in similarity_tuple:
        print('{} has cosine similarity of {}'.format(url, cos))
    
    print('---------------------------------------')
    print('The documets with top 10 similarities are as follows')

    similarity_tuple = sorted(similarity_tuple,
                              key=lambda x: x[1], reverse=True)

    index = 1
    for url, cos_val in similarity_tuple[:10]:
        print('{}. {} with cosine value of {}'.format(index, url, cos_val))
        index += 1


input_link=input("Enter the seed link : ").strip()

page = requests.get(input_link)
content = page.content

crawled_pages_directory_name = 'crawled_pages'
crawled_content_directory_name = 'crawled_content'

try:
    os.mkdir(crawled_pages_directory_name)
except FileExistsError:
    pass

try:
    os.mkdir(crawled_content_directory_name)
except FileExistsError:
    pass

base_dir = os.getcwd()

i = 0
soup = BeautifulSoup(content, features='lxml')
for link in soup.findAll('a', attrs={'href': re.compile("^http(s)?://")}):
    link = link.get('href')
    print('Visiting...', link)
    new_page = requests.get(link)
    new_content = str(new_page.content)

    store_page(i, new_content)

    para_text = []
    bs = BeautifulSoup(new_content)
    paras = soup.findAll('p')
    for para in paras:
        text = para.getText()
        text = re.sub('^<(a)|(/a).+>$', '', text)
        para_text.append(text)

    store_content(i, link, para_text)

    i += 1
    if i == 50:
        break


query = input('Enter your query: ').strip()
crawled_content_dir = base_dir + '/' + crawled_content_directory_name
similarity_dict = {}
iiii = 0

for file in os.listdir(crawled_content_dir):
    with open(file) as f:
        lines = f.readlines()[0]
        url = urls[iiii][0]
        vector1 = text_to_vector(query)
        vector2 = text_to_vector(lines)
        cosine = get_cosine(vector1, vector2)
        similarity_dict[url] = cosine
        iiii += 1

display_documents_and_their_similarity(similarity_dict)
