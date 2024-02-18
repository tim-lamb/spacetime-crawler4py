import pickle
from collections import defaultdict
import crawler_data
from simhash import *
from tokenizer import *

# For debugging the data
with open("data/pages.txt", 'rb') as page:
    urls = pickle.load(page)
with open("data/url_words.txt", 'rb') as page:
    url_words = pickle.load(page)
with open("data/word_freq_data.txt", 'rb') as page:
    words = pickle.load(page)
with open("data/subdomains.txt", 'rb') as page:
    subdomains = pickle.load(page)
with open("data/url_simhashes.txt", 'rb') as page:
    simhashes = pickle.load(page)
with open("data/checksum.txt", 'rb') as page:
    checksum = pickle.load(page)
with open("data/links.txt", 'rb') as page:
    links = pickle.load(page)
with open("data/404s.txt", 'rb') as page:
    check404 = pickle.load(page)


# sorted_urls = sorted(url_words.keys(),key=lambda x: url_words[x], reverse=True)
# for i in sorted_urls[0:30]:
#     print(i, ': ', url_words[i])
sorted_word = sorted(words.keys(), key = lambda x: words[x], reverse=True)
count = 0
for i in sorted_word:
    if count >= 50: break
    if len(i) >= 3:
        print(i, words[i])
        count += 1
# print(max(url_words,key=lambda x: url_words[x]))
#print(sorted(check404.keys(),key=lambda x: check404[x]))
#print(check404[r"https://www.informatics.uci.edu/very-top-footer-menu-items/people/"])