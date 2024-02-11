from collections import defaultdict
import pickle

# Idea for module-wide variables from: https://stackoverflow.com/questions/1977362/how-to-create-module-wide-variables-in-python

# Data for the crawler report
def init_crawler_data():
    # Entire set of URLS, Question #1
    global urls
    urls = set()

    # Set of URLs with number of words per page, Question #2
    global url_words
    url_words = defaultdict(int)

    # All the words parsed in the crawler and their frequency, Question #3
    global words
    words = defaultdict(int)

    # All ics.uci.edu subdomains and their occurences
    global subdomains
    subdomains = defaultdict(set)

    # Simhash for each page used to detect similarity
    global simhashes
    simhashes = dict()

def write_data(file):
    with open(file,'w') as f:
        with open("pages.txt", 'wb') as page:
            pickle.dump(urls, page)
        with open("url_words.txt", 'wb') as page:
            pickle.dump(url_words, page)
        with open("word_freq_data.txt", 'wb') as page:
            pickle.dump(words, page)
        with open("subdomains.txt", 'wb') as page:
            pickle.dump(subdomains, page)
        with open("url_simhashes.txt", 'wb') as page:
            pickle.dump(simhashes, page)
        f.write(f"Number of unique pages: {len(urls)}\n\n")
        f.write(f"Page with most words: {max(url_words.keys(),key=lambda x: url_words[x])}\n\n")
        f.write(f"Number of subdomains: {len(subdomains.keys())}\n\n")
        subd = subdomains.keys()
        subd = sorted(subd)
        for i in subd:
            f.write(f"{i}, {len(subdomains[i])}\n")


    