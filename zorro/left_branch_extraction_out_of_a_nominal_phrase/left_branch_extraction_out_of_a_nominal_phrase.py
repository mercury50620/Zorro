import random

from zorro.filter import collect_unique_pairs
from zorro.words import get_legal_words
from zorro import configs

import inflect

NUM_NOUNS = 50
NUM_ADJECTIVES = 50

template = '{} {} {} {} .'


def main():
    """
    example:
    *"cool he saw cars" vs "cool guys saw cars"
    "expensive he saw cars" vs "he saw expensive cars"

    """

    nouns_s_and_p = get_legal_words(tag='NN', second_tag='NNP')
    adjectives = get_legal_words(tag='JJ')
    excluded_verbs = ("said", "put", "became", "let", "based", "began", "came", "went", "thought", "died", "remained", "reported", "referred", "worked", "lived", "happened", "fell", "agreed", "failed", "arrived", "advanced", "resulted", "ran", "looked", "focused")
    verbs_past = get_legal_words(tag='VBD', exclude=excluded_verbs)
    humanity = (configs.Dirs.legal_words / 'humanity.txt').open().read().split()
    
    prns_nom = ["i", "you", "he", "she", "we", "they"]


    while True:

        # random choices
        _, noun_pl = random.choice(nouns_s_and_p)
        human_ = random.choice(humanity)
        plural = inflect.engine()
        human = plural.plural(human_)
        adj = random.choice(adjectives)
        verb = random.choice(verbs_past)
        prn = random.choice(prns_nom)


        # contrast is in number agreement between subject and copula
        yield template.format(adj, prn, verb, noun_pl)  # bad
        yield template.format(adj, human, verb, noun_pl)  # good
        yield template.format(adj, prn, verb, noun_pl)  # bad
        yield template.format(prn, verb, adj, noun_pl)  # good

if __name__ == '__main__':
    for n, s in enumerate(collect_unique_pairs(main)):
        print(f'{n//2+1:>12,}', s)
