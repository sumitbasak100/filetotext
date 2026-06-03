import re
import numpy as np

AI_PHRASES = [
    "in conclusion",
    "furthermore",
    "moreover",
    "it is important to note",
    "overall",
    "ultimately",
    "to summarize",
    "in summary",
    "to conclude",
    "when it comes to",
    "of course",
    "certainly",
    "seamlessly",
    "tailored",
    "comprehensive",
    "pivotal",
    "intricate"
]

TRANSITIONS = [
    "however",
    "therefore",
    "furthermore",
    "moreover",
    "additionally",
    "thus",
    "consequently",
    "overall",
    "ultimately"
]

HEDGES = [
    "it is important to note",
    "it should be noted",
    "it is worth mentioning",
    "one can argue",
    "it is clear that",
    "it is evident that"
]


def detect_ai_probability(text):

    text = text.lower()

    words = re.findall(r"\b[a-z]+\b", text)

    if len(words) < 30:
        return 0.5

    sentences = [
        s.strip()
        for s in re.split(r"[.!?]+", text)
        if s.strip()
    ]

    score = 0.0

    # vocabulary diversity
    unique_ratio = len(set(words)) / len(words)

    if unique_ratio < 0.45:
        score += 0.30
    elif unique_ratio < 0.55:
        score += 0.20

    # sentence consistency
    lengths = [len(s.split()) for s in sentences]

    if len(lengths) > 1:

        std = np.std(lengths)

        if std < 4:
            score += 0.25
        elif std < 8:
            score += 0.15

        avg_len = np.mean(lengths)

        if 12 <= avg_len <= 22:
            score += 0.10

    # AI phrases
    phrase_matches = sum(
        1 for phrase in AI_PHRASES
        if phrase in text
    )

    if phrase_matches >= 3:
        score += 0.35
    elif phrase_matches >= 1:
        score += 0.20

    # transitions
    transition_count = sum(
        text.count(word)
        for word in TRANSITIONS
    )

    if transition_count >= 3:
        score += 0.15

    # hedging
    hedge_count = sum(
        1 for phrase in HEDGES
        if phrase in text
    )

    score += min(hedge_count * 0.05, 0.15)

    # repetition
    counts = {}

    for word in words:
        counts[word] = counts.get(word, 0) + 1

    repeated = sum(
        1 for count in counts.values()
        if count >= 4
    )

    if repeated > len(words) * 0.02:
        score += 0.10

    probability = score / 1.35

    probability = max(0.05, min(probability, 0.95))

    return round(probability, 3)
