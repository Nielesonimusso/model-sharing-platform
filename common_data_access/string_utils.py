import string

from jellyfish import damerau_levenshtein_distance


def are_almost_equal(s1: str, s2: str, match_case=False, mismatch_ratio=0.1, strip=True) -> bool:
    if s1 is None and s2 is None:
        return False

    s1 = '' if s1 is None else s1
    s2 = '' if s2 is None else s2

    s1 = s1 if match_case else s1.lower()
    s2 = s2 if match_case else s2.lower()

    s1 = s1.strip() if strip else s1
    s2 = s2.strip() if strip else s2

    distance = damerau_levenshtein_distance(s1, s2)
    avg_len = len(s1 + s2) / 2
    # are equal if distance is less than 10% or the avg. length
    return distance / avg_len <= mismatch_ratio


def to_camel_case(s: str) -> str:
    if s is None: return s

    punct_and_space = string.punctuation + string.whitespace
    camel_cased = ''.join([f'{m[0].upper()}{m[1:]}' if len(m) else '' for m in
                           s.strip().translate(str.maketrans(punct_and_space, '_' * len(punct_and_space))).split('_')])
    return camel_cased[0].lower() + camel_cased[1:]
