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




    