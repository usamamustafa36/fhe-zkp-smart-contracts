from collections import Counter
import math

def shannon_entropy(data):
    if isinstance(data, str):
        data = data.encode()
    counts = Counter(data)
    total = len(data)
    entropy = -sum(count / total * math.log2(count / total) for count in counts.values())
    return entropy
