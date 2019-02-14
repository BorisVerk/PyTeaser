from goose3 import Goose
from collections import Counter
import re
import sys

with open("stopwords/en.txt") as f:
    stop_words = {line.rstrip("\n") for line in f if line}
    stop_words.update(["-", " ", ",", "."])
ideal_sentence_length = 20

grab_link = Goose().extract


def summarize_url(url):
    try:
        article = grab_link(url=url)
    except IOError as e:
        print("Couldn't fetch the URL:", e, file=sys.stderr)
        return
    except ValueError as e:
        print("Goose failed to extract article from url:", e, file=sys.stderr)
        return

    if article and article.cleaned_text and article.title:
        return summarize(article.title, article.cleaned_text)


def summarize(title, text):
    sentences = split_sentences(text)
    keys = keywords(text)
    title_words = split_words(title)

    if len(sentences) <= 5:
        return sentences

    # score setences, and use the top 5 sentences
    sentence_ranks = score(sentences, title_words, keys)
    #print(sentence_ranks)
    return [sentence for sentence, score in sentence_ranks[:5]]


def score(sentences, title_words, keywords):
    num_sentences = len(sentences)
    sentence_scores = []

    for i, sentence in enumerate(sentences):
        words = split_words(sentence)

        # weighted average of scores from four categories
        scores = [
            title_score(title_words, words),
            (sbs(words, keywords) + dbs(words, keywords)),
            length_score(words),
            sentence_position(i + 1, num_sentences),
        ]
        weights = [1.5, 10, 1, 1]
        score = sum(score * weight / 4 for score, weight in zip(scores, weights))

        sentence_scores.append((sentence, score))

    # sort sentences by score in descending order
    return sorted(sentence_scores, key=lambda x: x[1], reverse=True)


def sbs(words, keywords):
    score = sum(keywords[word] for word in words if word in keywords)
    if score == 0:
        return 0
    return (1 / abs(len(words)) * score) / 10


def dbs(words, keywords):
    if not words:
        return 0

    summ = 0
    first = []
    second = []

    for i, word in enumerate(words):
        if word in keywords:
            score = keywords[word]
            if first == []:
                first = [i, score]
            else:
                second = first
                first = [i, score]
                dif = first[0] - second[0]
                summ += (first[1] * second[1]) / (dif ** 2)

    # number of intersections
    k = len(set(keywords.keys()).intersection(set(words))) + 1
    return 1 / (k * (k + 1.0)) * summ


def split_words(text):
    # split a string into an array of words
    try:
        text = re.sub(r"[^\w ]", "", text)  # strip special chars
        return [x.strip(".").lower() for x in text.split()]
    except TypeError:
        print("Error while splitting characters")
        return None


def keywords(text):
    """get the top 10 keywords and their frequency scores
    ignores blacklisted words in stop_words,
    counts the number of occurrences of each word
    """
    words = split_words(text)
    freq = Counter(word for word in words if word not in stop_words)
    return {word: count / len(words) * 1.5 + 1 for word, count in freq.most_common(10)}


def split_sentences(text):
    """
    The regular expression matches all sentence ending punctuation and splits the string at those points.
    At this point in the code, the list looks like this ["Hello, world", "!" ... ]. The punctuation and all quotation marks
    are separated from the actual text. The first s_iter line turns each group of two items in the list into a tuple,
    excluding the last item in the list (the last item in the list does not need to have this performed on it). Then,
    the second s_iter line combines each tuple in the list into a single item and removes any whitespace at the beginning
    of the line. Now, the s_iter list is formatted correctly but it is missing the last item of the sentences list. The
    second to last line adds this item to the s_iter list and the last line returns the full list.
    """

    sentences = re.split('(?<![A-ZА-ЯЁ])([.!?]"?)(?=\s+"?[A-ZА-ЯЁ])', text)
    s_iter = zip(*[iter(sentences[:-1])] * 2)
    s_iter = ["".join(y).lstrip() for y in s_iter]
    s_iter.append(sentences[-1].lstrip())
    return s_iter


def length_score(sentence):
    return 1 - abs(ideal_sentence_length - len(sentence)) / ideal_sentence_length


def title_score(title, sentence):
    title = [x for x in title if x not in stop_words]

    if not title:
        return 0

    words_in_title = sum(True for x in sentence if x not in stop_words and x in title)
    return words_in_title / len(title)


def sentence_position(i, size):
    """different sentence positions indicate different
    probability of being an important sentence"""

    normalized = i * 1.0 / size
    if 0 < normalized <= 0.1:
        return 0.17
    elif 0.1 < normalized <= 0.2:
        return 0.23
    elif 0.2 < normalized <= 0.3:
        return 0.14
    elif 0.3 < normalized <= 0.4:
        return 0.08
    elif 0.4 < normalized <= 0.5:
        return 0.05
    elif 0.5 < normalized <= 0.6:
        return 0.04
    elif 0.6 < normalized <= 0.7:
        return 0.06
    elif 0.7 < normalized <= 0.8:
        return 0.04
    elif 0.8 < normalized <= 0.9:
        return 0.04
    elif 0.9 < normalized <= 1.0:
        return 0.15
    else:
        return 0


def SummarizeUrl(url):
    import warnings

    warnings.warn(
        "SummarizeUrl(url) has been deprecated. "
        "Please use summarize_url(title, text) (with a lower case letter) instead.",
        DeprecationWarning,
    )

    return summarize_url(url)


def Summarize(title, text):
    import warnings

    warnings.warn(
        "Summarize(title, text) using a capital letter has been deprecated. "
        "Please use summarize(title, text) (with a lower case letter) instead.",
        DeprecationWarning,
    )

    return summarize(title, text)
