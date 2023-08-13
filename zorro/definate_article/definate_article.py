import random

from zorro.filter import collect_unique_pairs
from zorro.words import get_legal_words
from zorro import configs

# todo 全部
#templateをbad/goodで分けているのは、単語数が変わってしまうため

template1 = {
    'b': '{pn_nom_names} broke window .',
    'g': '{pn_nom_names} broke {det} window .',
}

template2 = {
    'b': '{animates} broke {pn_acc} .',
    'g': '{det} {animates} broke {pn_acc} .',
}

template3 = {
    'b': '{humans} is {jj} .',
    'g': '{det} {humans} is {jj} .',
}

paradigm = 'definite_article'


def main():
    """
    examples:
    *"he broke window ." vs. "he broke the window."
    *"cat broke it ." vs. "the cat broke the window."
    *"the girl is kind ." vs. "girl is kind ."

    """

    determiners = ["the", "this", "that", "my", "your", "his", "her", "our", "their"] #a(n)は扱いが面倒なので無し

    animates = (configs.Dirs.legal_words / 'animates.txt').open().read().split()
    humans = (configs.Dirs.legal_words / 'humanity.txt').open().read().split()
    pn_nom = ["i", "you", "he", "she", "we", "they"]
    names = (configs.Dirs.legal_words / 'names.txt').open().read().split()
    pn_nom_names = pn_nom + names
    pn_acc = ["it", "them"]
    adjectives = (configs.Dirs.legal_words / 'adj_goes_with_girl.txt').open().read().split()

    while True:

        # random choices
        slot2filler = {
            'animates': random.choice(animates),
            "humans": random.choice(humans),
            'det': random.choice(determiners),
            'pn_nom_names': random.choice(pn_nom_names),
            'pn_acc': random.choice(pn_acc),
            'jj': random.choice(adjectives)
        }

        yield template1['b'].format(**slot2filler)  
        yield template1['g'].format(**slot2filler)

        yield template2['b'].format(**slot2filler)
        yield template2['g'].format(**slot2filler)

        yield template3['b'].format(**slot2filler)
        yield template3['g'].format(**slot2filler)

if __name__ == '__main__':
    for n, s in enumerate(collect_unique_pairs(main)):
        print(f'{n//2+1:>12,}', s)
