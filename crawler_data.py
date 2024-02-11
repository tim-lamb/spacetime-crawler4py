from collections import defaultdict
import pickle

# Idea for module-wide variables from: https://stackoverflow.com/questions/1977362/how-to-create-module-wide-variables-in-python
def init_load_save():
    global LOAD_SAVE
    LOAD_SAVE = False

# Data for the crawler report
def init_crawler_data():
    # Entire set of URLS, Question #1
    global urls
    # Set of URLs with number of words per page, Question #2
    global url_words
    # All the words parsed in the crawler and their frequency, Question #3
    global words
    # All ics.uci.edu subdomains and their occurences
    global subdomains
    # Simhash for each page used to detect similarity
    global simhashes
    # Sum of all bytes for each page to detect exact duplicates
    global checksum

    if LOAD_SAVE:
        with open("pages.txt", 'rb') as page:
            urls = pickle.load(page)
        with open("url_words.txt", 'rb') as page:
            url_words = pickle.load(page)
        with open("word_freq_data.txt", 'rb') as page:
            words = pickle.load(page)
        with open("subdomains.txt", 'rb') as page:
            subdomains = pickle.load(page)
        with open("url_simhashes.txt", 'rb') as page:
            simhashes = pickle.load(page)
        with open("checksum.txt", 'rb') as page:
            checksum = pickle.load(page)
    else:
        urls = set()
        url_words = defaultdict(int)
        words = defaultdict(int)
        subdomains = defaultdict(set)
        simhashes = dict()
        checksum = dict()

def write_data(file):
        try:
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
            with open("checksum.txt", 'wb') as page:
                pickle.dump(checksum, page)
            with open(file,'w') as f:
                f.write(f"Number of unique pages: {len(urls)}\n\n")
                f.write(f"Page with most words: {max(url_words.keys(),key=lambda x: url_words[x])}\n\n")
                f.write(f"Number of subdomains: {len(subdomains.keys())}\n\n")
                subd = subdomains.keys()
                subd = sorted(subd)
                for i in subd:
                    f.write(f"{i}, {len(subdomains[i])}\n")
        except:
            # When pickling fails
            pass
   