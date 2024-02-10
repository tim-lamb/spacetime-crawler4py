from collections import defaultdict
import re
# Runs in O(n) time with respect to the document length
STOPWORDS = r"\b(a|about|above|after|again|against|all|am|an|and|any|are|aren't|as|at|be|because|been|before|being|below|between|both|but|by|can't|cannot|could|couldn't|did|didn't|do|does|doesn't|doing|don't|down|during|each|few|for|from|further|had|hadn't|has|hasn't|have|haven't|having|he|he'd|he'll|he's|her|here|here's|hers|herself|him|himself|his|how|how's|i|i'd|i'll|i'm|i've|if|in|into|is|isn't|it|it's|its|itself|let's|me|more|most|mustn't|my|myself|no|nor|not|of|off|on|once|only|or|other|ought|our|ours|ourselves|out|over|own|same|shan't|she|she'd|she'll|she's|should|shouldn't|so|some|such|than|that|that's|the|their|theirs|them|themselves|then|there|there's|these|they|they'd|they'll|they're|they've|this|those|through|to|too|under|until|up|very|was|wasn't|we|we'd|we'll|we're|we've|were|weren't|what|what's|when|when's|where|where's|which|while|who|who's|whom|why|why's|with|won't|would|wouldn't|you|you'd|you'll|you're|you've|your|yours|yourself|yourselves)\b"
def tokenize(text):
    """
    Get all tokens from a document specified by a path

    Parameters:
    path: String of a system path

    Return:
    tokens: List of tokens
    """
    content = text.lower()
    tokens = []
    tokenStr = ""
    content = re.sub(STOPWORDS, '', content)
    # Tokenize algorith that goes through each character, should be O(n) with respect to # of characters
    for c in content+" ":
        try:
            if (re.match("[a-zA-Z|0-9]", c) != None):
                tokenStr += c
                continue
            elif tokenStr != "":
                tokens.append(tokenStr)
                tokenStr = ""
        except:
            pass


    return tokens

# Runs in O(n) time with respect to the number of tokens
def computeWordFrequencies(tokens):
    """
    Count the frequency of all tokens.

    Parameters:
    tokens: List of all tokens

    Return:
    count: Dict<Token, Int> dict of tokens and its # of occurences
    """
    # Default dict with default value for each token being 0
    count = defaultdict(int)

    # Go through each token and increment its value in the dict by 1, O(n) time
    for token in tokens:
        count[token] += 1
    return count

# Should run in O(n log n) time with respect to number of unique tokens
def printTokens(count, file):
    """
    Print out the token and its number of occurences

    Parameters:
    count: Dict<Token, Int> of tokens and its # of occurences

    Return:
    none
    """
    # Get all the tokens and sort by occurences
    f = open(file, 'w')
    keys = count.keys()
    keys = sorted(keys, key=lambda x: (-count[x], x))[:50] # Python sorted() runs in O(n log n) time

    # O(n) time with number of keys
    for key in keys:
        f.write(f"{key} {count[key]}\n")
    f.close()

# tokens = tokenize("one.txt")
# print(tokens)
# printTokens(computeWordFrequencies(tokens))