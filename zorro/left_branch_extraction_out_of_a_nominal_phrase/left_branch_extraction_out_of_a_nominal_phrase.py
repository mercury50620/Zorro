import random

from zorro.filter import collect_unique_pairs
from zorro.words import get_legal_words
from zorro import configs
from zorro import make_verb_noun_dict
import inflect
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
p = inflect.engine()
verb_noun_dict = make_verb_noun_dict.make_verb_noun_dict()
adj_noun_dict = make_verb_noun_dict.make_adj_noun_dict()
bare_past_dict = make_verb_noun_dict.make_bare_past_dict()

NUM_NOUNS = 50
NUM_ADJECTIVES = 50

template = '{} {} {} {} .'


def main():
    """
    example:
    "expensive he saw cars" vs "he saw expensive cars"

    """
    nouns = (configs.Dirs.legal_words / 'legal_nouns.txt').open().read().split()
    adjectives = (configs.Dirs.legal_words / 'legal_adjectives.txt').open().read().split()
    #excluded_verbs = ("said", "put", "became", "let", "based", "began", "came", "went", "thought", "died", "remained", "reported", "referred", "worked", "lived", "happened", "fell", "agreed", "failed", "arrived", "advanced", "resulted", "ran", "looked", "focused")
    #verbs_past = get_legal_words(tag='VBD', exclude=excluded_verbs)
    verbs = (configs.Dirs.legal_words / 'legal_verbs.txt').open().read().split()

    prns_nom = ["i", "you", "he", "she", "we", "they"]

    count = 0
    while True:
        # random choices
        #_, noun_pl = random.choice(nouns_s_and_p)
        prn = random.choice(prns_nom)
        while True:
            verb = random.choice(verbs)
            adj = random.choice(adjectives)
            if len(set(verb_noun_dict.get(verb, []))&set(nouns)) == 0 or len(set(adj_noun_dict.get(adj, []))&set(nouns)) == 0:
                continue
            else:
                possible_noun_from_verb = set(verb_noun_dict.get(verb, []))
                possible_noun_from_adj = set(adj_noun_dict.get(adj, []))
                possible_noun_set = possible_noun_from_verb & possible_noun_from_adj

                if  len(possible_noun_set) == 0:
                    continue
                else:
                    noun = random.choice(list(possible_noun_set))
                    count += 1
                    noun_pl = p.plural(noun)
                    print(noun, adj)
                    print(count)
                    break
       

        verb_p = bare_past_dict.get(verb)
        if verb_p == None:
            continue
        # contrast is in number agreement between subject and copula
        yield template.format(adj, prn, verb_p, noun_pl)  # bad
        yield template.format(prn, verb_p, adj, noun_pl)  # good

if __name__ == '__main__':
    for n, s in enumerate(collect_unique_pairs(main)):
        print(f'{n//2+1:>12,}', s)
