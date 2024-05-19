N = {"pol": 0, "eng": 0}  # sum of frequencies of words
WORDS = {"pol": {}, "eng": {}}
ALPHA = {"pol": "aąbcćdeęfghijklłmnńoóprsśtuwyzźż", "eng": "abcdefghijklmnopqrstuvwxyz"}
COMMON_MISTAKES = {
    "pol": (
        ("a", "ą"),
        ("c", "ć"),
        ("e", "ę"),
        ("i", "j"),
        ("l", "ł"),
        ("t", "ł"),
        ("m", "n"),
        ("o", "ó"),
        ("s", "ś"),
        ("z", "ź"),
        ("z", "ż"),
    ),
    "eng": (()),
}


def load(lang):
    """Loads the word list for lang if it hasn't been loaded previously."""
    with open(f"./image_reader/static/word_lists/{lang}.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            word, freq = line.split(" ")
            WORDS[lang][word] = int(freq)
            N[lang] += int(freq)


def known(word_list, lang):
    """Return the set of words that appear in word_list and are known (appear in WORDS)"""
    return set(word for word in word_list if word in WORDS[lang].keys())


def leven1(word, lang):  # levenshtein distance
    """Return the set of words that are 1 edit away from word."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [l + r[1:] for (l, r) in splits if len(r) > 0]
    transposes = [l + r[1] + r[0] + r[2:] for (l, r) in splits if len(r) > 1]
    replaces = [l + c + r[1:] for (l, r) in splits if len(r) > 0 for c in ALPHA[lang]]
    inserts = [l + c + r for (l, r) in splits for c in ALPHA[lang]]

    return set(deletes + transposes + replaces + inserts)


def leven2(word, lang):
    """Return the set of words that are 2 edits away from word."""
    words1 = leven1(word, lang)
    words2 = set()
    for one_edit in words1:
        words2 = words2 | leven1(one_edit, lang)

    return words2


def candidates(word, lang):
    """Return a list of possible fixes for a misspelled word."""
    return known(set([word]), lang) | known(leven1(word, lang), lang)


def similarity(w1, w2, lang):
    """Return the 'similarity' of words w1 and w2 (the higher the similarity, the more likely that w1 has been
    a result of misspelling w2)."""
    pr = WORDS[lang][w1] / N[lang]
    mult = 1
    if len(w1) == len(w2):
        for i in range(len(w1)):
            if (w1[i], w2[i]) in COMMON_MISTAKES[lang] or (
                w2[i],
                w1[i],
            ) in COMMON_MISTAKES[lang]:
                mult += 0.1

    return pr * mult


def correction(word, lang):
    """Return the mosts probable correction of word."""
    cand = candidates(word, lang)
    if len(cand) == 0:
        return word
    return max(cand, key=lambda w: similarity(w, word, lang))


def spellcheck(text, lang):
    """Return the text after applying spelling fixes."""
    if len(WORDS[lang]) == 0:
        load(lang)

    whitespaces = []
    cnt = 0
    for c in text:
        if c.isspace():
            if cnt == 0:
                whitespaces.append("")
            cnt += 1
            whitespaces[-1] += c
        else:
            cnt = 0
    whitespaces.append("")

    words = text.split()
    fixed = ""
    for i, word in enumerate(words):
        mask = [c.isupper() for c in word]
        interpunction = ""
        if word[-1] in (
            ",",
            ".",
            ";",
            ":",
            '"',
            "'",
            "(",
            ")",
            "[",
            "]",
            "-",
            "?",
            "!",
        ):
            interpunction = word[-1]
            word = word[:-1]
        correct = word.lower()
        if correct not in WORDS[lang].keys():
            correct = correction(word, lang)

        final = list(correct)
        for j in range(len(correct)):
            if j < len(mask) and mask[j]:
                final[j] = final[j].upper()
        fixed += f"{"".join(final)}{interpunction}{whitespaces[i]}"

    return fixed


if __name__ == "__main__":
    text = input()
    print(spellcheck(text, "pol"))
