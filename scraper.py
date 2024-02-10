import re
from urllib.parse import urlparse, urldefrag, urljoin, urlunparse
from bs4 import BeautifulSoup
from tokenizer import *
import crawler_data


# Specified domains in regex pattern
ALLOWED_URLS_PATTERN = r".*\.ics\.uci\.edu\/[^#]*" \
                        + r"|.*\.cs\.uci\.edu\/[^#]*" \
                        + r"|.*\.informatics\.uci\.edu\/[^#]*" \
                        + r"|.*\.stat\.uci\.edu\/[^#]*"

def scraper(url, resp):
    links = extract_next_links(url, resp)
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

    # with open("debug.txt", 'a') as f:
    #     f.write("base url:")
    #     f.write(base)
    #     f.write('\n')
    #     f.write("old url:")
    #     f.write(url)
    #     f.write('\n')
    #     f.write("new url:")
    #     f.write(urldefrag(new_url)[0])
    #     f.write('\n\n')

    # Defragment and return
    return urldefrag(new_url)[0]


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
    if re.match(r"(ics\.uci\.edu)", parsed.netloc):
        crawler_data.subdomains[parsed.netloc] += 1

    # Check if URL could be opened successfully
    if resp.status != 200:
        return list()
    
    # Check that URL has data, otherwise return empty list
    if resp.raw_response == None or resp.raw_response.content == None:
        return list()
    
    # Parse the contents of the page
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # Update the overall data
    tokens = []
    for text in soup.stripped_strings:
        tokens += tokenize(text)
    update_frequencies(tokens, url)

    # Get all the URLs in a page
    extracted = []
    for site in soup.find_all('a'):
        found_url = site.get('href')
        if found_url == None: continue
        new_url = fix_url(url, found_url)
        extracted.append(new_url)
    
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # Check if the URL is part of allowed domains
        if not re.match(ALLOWED_URLS_PATTERN, parsed.path.lower()):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
