import hashlib

NUM_BITS = 32

def create_hash(word):
    # Create a n bit hash value for a word
    return hashlib.md5(word).digest()[:NUM_BITS//8]

def create_vector(count):
    # Create the n-dimension vector from word list
    bit_vec = dict()
    for i in sorted(count.keys(), key=lambda x: count[x]):
        bit_vec[i] = bin(int.from_bytes(create_hash(i.encode()), 'little'))[2:].zfill(NUM_BITS)
    return bit_vec

def generate_fingerprint(bit_vec, count):
    # Generate the fingerprint for similarity check
    keys = sorted(count.keys(),key=lambda x: count[x])
    weighted = []
    for i in range(NUM_BITS):
        val = 0
        for b in keys:
            if bit_vec[b][i] == '0':
                val -= count[b]
            else:
                val += count[b]
        weighted.append(val)
    return list(map(lambda x: 0 if x < 0 else 1, weighted))

def compare_hashes(hash_a, hash_b):
    similar = 0
    for i in range(len(hash_a)):
        similar += 1 if hash_a[i] == hash_b[i] else 0
    return similar/len(hash_a)

def simhash(count):
    # Generate a simhash for a count of tokens
    bit_vec = create_vector(count)
    shash = generate_fingerprint(bit_vec, count)
    return shash

# bit_vec = {"tropical":      "01100001",
#            "fish":          "10101011",
#            "include":       "11100110",
#            "found":         "00011110",
#            "environments":  "00101101",
#            "around":        "10001011",
#            "world":         "00101010",
#            "including":     "11000000",
#            "both":          "10101110",
#            "freshwater":    "00111111",
#            "salt":          "10110101",
#            "water":         "00100101",
#            "species":       "11101110"}

# count = {"tropical":        2,
#            "fish":          2,
#            "include":       1,
#            "found":         1,
#            "environments":  1,
#            "around":        1,
#            "world":         1,
#            "including":     1,
#            "both":          1,
#            "freshwater":    1,
#            "salt":          1,
#            "water":         1,
#            "species":       1}
# hash_a = generate_fingerprint(bit_vec, count)

# string_one = "one two three four five six seven eight nine ten"
# string_two = "one two three four five"
# count_one = tokenizer.computeWordFrequencies(tokenizer.tokenize(string_one))
# count_two = tokenizer.computeWordFrequencies(tokenizer.tokenize(string_two))
# hash_one = simhash(count_one)
# hash_two = simhash(count_two)
# print(compare_hashes(hash_one, hash_two))
