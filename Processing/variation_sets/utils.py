"""Variation sets utils."""

from itertools import islice
import difflib


def window(seq, n=2):
    """Returns a sliding window (of width n) over data from the iterable s
    -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ..."""

    # TODO: this method of extracting pairs has a fence post problem
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def levenshtein_dist(s1, s2):
    """Input two strings, returns levenstein distance between the two"""

    s1 = ' ' + s1
    s2 = ' ' + s2
    d = {}
    S1 = len(s1)
    S2 = len(s2)
    for i in range(S1):
        d[i, 0] = i
    for j in range(S2):
        d[0, j] = j
    for j in range(1, S2):
        for i in range(1, S1):
            if s1[i] == s2[j]:
                d[i, j] = d[i - 1, j - 1]
            else:
                d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + 1)
    return d[S1 - 1, S2 - 1]


def levenshtein(A, B, match_type):
    """ 2 lists of strings and an integar
    returns the number of strings in common, adjusted by levenstein distance"""
    match_count = 0
    for word in A:
        if isinstance(word, type(None)):
            continue

        for word_ in B:
            if isinstance(word_, type(None)):
                continue
            if levenshtein_dist(word, word_) <= match_type:
                match_count += 1
                break
    return match_count


def matches_wrapper(utterance_A, utterance_B, match_type, minimum_matches):
    """Input two lists of strings, a minimum number of matches,
    and either None, Integar or Float
    Returns: whether the required number of matches has been met for which ever type:
    None: intersection of set of both lists
    Integar: levenstein distance
    Float: Python's difflib"""

    if isinstance(match_type, type(None)):
        if len(set(utterance_A).intersection(set(utterance_B))) >= minimum_matches:
            return True

    # TODO: revisit this
    elif isinstance(match_type, int):
        if levenshtein(utterance_A, utterance_B, match_type) >= minimum_matches:
            return True

    elif isinstance(match_type, float):
        # difflib returns 1.0 for space, so skip any utterances that are blank, i.e. no N or V match
        if len(utterance_A) == 0 and len(utterance_B) == 0:
            return False

        matches = 0
        for item in utterance_A:
            for i in utterance_B:
                if difflib.SequenceMatcher(lambda x: x == ' ', item, i).ratio() >= match_type:
                    matches += 1
        # TODO: this is wrong, i.e. for the multiple match scenario, i.e. at least two matches per VS, but this simply iterates and counts
        if matches >= minimum_matches:
            return True
        else:
            return False

    """ 
    elif isinstance(match_type, float):
        # difflib returns 1.0 for space, so skip any utterances that are blank, i.e. no N or V match
        if len(utterance_A) == 0 and len(utterance_B) == 0:
            return False
        utterance_A = ' '.join([i for i in utterance_A if i])
        utterance_B = ' '.join([i for i in utterance_B if i])
        distance = difflib.SequenceMatcher(lambda x: x == ' ', utterance_A, utterance_B).ratio()
        if distance >= match_type:
            return True
    """


def matches_anchor(it, minimum_matches, match_type):
    """Given an iterator, returns count of all variation sets found using the anchor algorithm."""
    matches = 0
    utterances_to_dump = list()

    for i in it:
        utterances = iter(i)
        first = next(utterances)
        for utterance in utterances:
            if matches_wrapper(first, utterance, match_type, minimum_matches):
                matches += 1
                utterances_to_dump.append((first, utterance))
                break
    return matches, utterances_to_dump


def matches_incremental(it, minimum_matches, match_type):
    """Given an iterator returns the minimum matches. Note that any changes here must be added to
    varseta_accuracy_test.py."""
    matches = 0
    utterances_to_dump = list()
    for i in it:
        pairs = window(i)
        for i, j in pairs:
            if matches_wrapper(i, j, match_type, minimum_matches):
                utterances_to_dump.append((i, j))
                matches += 1
    return matches, utterances_to_dump


def get_exact_repetitions(utterances, n):
    """Returns exact repetitions of length n."""
    exact_repetitions = []
    windows = window(utterances, n)
    for t in windows:
        if len(t) != len(set(t)):
            exact_repetitions.append(t)
    return exact_repetitions
