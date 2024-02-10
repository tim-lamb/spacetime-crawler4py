from collections import defaultdict

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
    subdomains = defaultdict(int)

def write_data(file):
    with open(file,'w') as f:
        f.write(f"Number of unique pages: {len(urls)}\n\n")
        f.write(f"Page with most words: {max(url_words.keys(),key=lambda x: url_words[x])}\n\n")
        f.write(f"Number of subdomains: {len(subdomains.keys())}\n\n")
        subd = subdomains.keys()
        subd = sorted(subd)
        for i in subd:
            f.write(f"{i}, {subdomains[i]}\n")


    