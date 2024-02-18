from bs4 import BeautifulSoup
from tokenizer import *
from simhash import *
import re

# name1 = "diff1.html"

# name2 = "diff2.html"
# content1 = BeautifulSoup(open(name1))
# content2 = BeautifulSoup(open(name2))
# tokens1 = []
# tokens2 = []
# for text in content1.stripped_strings:
#     tokens1 += tokenize(text)
# for text in content2.stripped_strings:
#     tokens2 += tokenize(text)

# print(len(set(tokens1)))
# print(len(set(tokens2)))
# count1 = computeWordFrequencies(tokens1)
# count2 = computeWordFrequencies(tokens2)
# shash1 = simhash(count1)
# shash2 = simhash(count2)
# print(compare_hashes(shash1,shash2))
pattern = r".*(do=diff).*|.*(rev=).*"
string = r"http://sli.ics.uci.edu/Classes/2012W-178?action=download&upname=L17.pdf"
m = re.match(pattern,string)
print(m.group(0))