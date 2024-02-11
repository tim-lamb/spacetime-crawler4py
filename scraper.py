import re
from urllib.parse import urlparse, urldefrag, urljoin, urlunparse
from bs4 import BeautifulSoup
from tokenizer import *
import crawler_data
from simhash import *
import urllib.robotparser


# Specified domains in regex pattern
ALLOWED_URLS_PATTERN = r".*\.ics\.uci\.edu\/[^#]*" \
                        + r"|.*\.cs\.uci\.edu\/[^#]*" \
                        + r"|.*\.informatics\.uci\.edu\/[^#]*" \
                        + r"|.*\.stat\.uci\.edu\/[^#]*"
# With groups
PATTERN = r".*(\.ics\.uci\.edu\/)[^#]*|.*(\.cs\.uci\.edu\/)[^#]*|.*(\.informatics\.uci\.edu\/)[^#]*|.*(\.stat\.uci\.edu\/)[^#]*"

# Parse the robots.txt files
ROBOT = {
    ".ics.uci.edu/": urllib.robotparser.RobotFileParser("https://www.ics.uci.edu/robots.txt"),
    ".cs.uci.edu/": urllib.robotparser.RobotFileParser("https://www.cs.uci.edu/robots.txt"),
    ".informatics.uci.edu/": urllib.robotparser.RobotFileParser("https://www.informatics.uci.edu/robots.txt"),
    ".stat.uci.edu/": urllib.robotparser.RobotFileParser("https://www.stat.uci.edu/robots.txt")
    }
for i in ROBOT.keys(): ROBOT[i].read()

SITEMAP_CHECKED = False

def scraper(url, resp):
    links = extract_next_links(url, resp)

    # Check sitemaps for links
    sitemaps = []
    global SITEMAP_CHECKED
    if not SITEMAP_CHECKED:
        for domain in ROBOT.keys():
            ROBOT[domain].read()
            sites = ROBOT[domain].site_maps()
            sitemaps += sites if sites != None else []
        SITEMAP_CHECKED = True
        return [link for link in links if is_valid(link)] + sitemaps
    else:
        return [link for link in links if is_valid(link)]

def update_frequencies(tokens, url):
    # Update the crawler data word frequencies
    for token in tokens:
        crawler_data.words[token] += 1
        crawler_data.url_words[url] += 1
    printTokens(crawler_data.words, "frequencies.txt")

def fix_url(base, url):
    # Fixes URLs in the wrong format (relative, missing scheme, fragments)
    base_parsed = urlparse(base+'/')
    url_parsed = urlparse(url)

    # If relative URL with whole path
    if url_parsed.netloc == '' and url_parsed.path.startswith('/'):
        url_parsed = url_parsed._replace(netloc = base_parsed.netloc)
    
    # If relative URL with ../
    if url_parsed.netloc == '' and url_parsed.path.startswith('../'):
        parent_path = '/'.join(base_parsed.path[1:-1].split("/")[:-url.count('../')])
        ind = url_parsed.path.rfind('../')
        new_path = parent_path+url[ind+2:]
        url_parsed = url_parsed._replace(netloc = base_parsed.netloc)
        url_parsed = url_parsed._replace(path = new_path)
    
    # If relative URL to the base
    if url_parsed.netloc == '':
        url_parsed = base_parsed._replace(path = base_parsed.path + url_parsed.path)

    # If missing scheme
    if url_parsed.scheme == '':
        url_parsed = url_parsed._replace(scheme=base_parsed.scheme)
    
    new_url = url_parsed.geturl()

    # Defragment and return
    return urldefrag(new_url)[0]

def check_similarity(url, shash):
    # Check similarity with given page against all other urls
    while True:
        try:
            for i in crawler_data.simhashes.keys():
                if i == url:
                    continue
                # If 90% similar return True
                if compare_hashes(shash, crawler_data.simhashes[i]) > 0.80:
                    return True
            return False
        except RuntimeError:
            continue

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    crawler_data.urls.add(url)
    parsed = urlparse(url)
    if re.match(r".*(\.ics\.uci\.edu).*", parsed.netloc):
        crawler_data.subdomains[parsed.netloc].add(url)

    # Check if URL could be opened successfully
    if resp.status != 200:
        return list()
    
    # Check that URL has data, otherwise return empty list
    if resp.raw_response == None or resp.raw_response.content == None:
        return list()
    
    # Check for the size of the file, avoid pages larger than 5MB
    if len(resp.raw_response.content) > 5000000:
        return list()

    # Check if exact duplicate using checksum method
    checksum = sum(resp.raw_response.content)
    if checksum in crawler_data.checksum.values(): return list()
    else:
        crawler_data.checksum[url] = checksum

    # Parse the contents of the page
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # Update the overall data
    tokens = []
    for text in soup.stripped_strings:
        tokens += tokenize(text)

    # Avoid files with low information, could be large or small, not enough unique tokens or tokens all small
    if len(set(tokens)) <= 10 or max(map(len,tokens)) <= 5:
        return list()
    update_frequencies(tokens, url)

    # Create simhash for the url
    count = computeWordFrequencies(tokens)
    shash = simhash(count)
    crawler_data.simhashes[url] = shash

    # Check if near duplicate
    if check_similarity(url, shash):
        return list()

    
    # Get all the URLs in a page
    extracted = []
    for site in soup.find_all('a'):
        found_url = site.get('href')
        if found_url == None: continue
        new_url = fix_url(url, found_url)
        extracted.append(new_url)
    return extracted

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # Check if the URL is part of allowed domains
        if not re.match(ALLOWED_URLS_PATTERN, url.lower()):
            return False
        
        # Check robots.txt
        domain = re.match(PATTERN, url)
        if domain == None:
            domain = re.match(PATTERN, url+'/')
        for i in domain.groups():
            if i != None:
                domain = i
                break
        if not ROBOT[domain].can_fetch('*', url):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|apk|war|ppsx)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
