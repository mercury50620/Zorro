import random
import inflect

from zorro.filter import collect_unique_pairs
from zorro.words import get_legal_words
from zorro.counterbalance import find_counterbalanced_subset
from zorro import configs
#todo シード以外全部
template1 = {
    'b': 'from which {} did {} {} {} ?',
    'g': 'in which {} did {} {} {} ?',
}

template2 = {
    'b': 'about whom did {} {} {} ?',
    'g': 'for whom did {} {} {} ?',
}



def main():
    """
    example:
    "*from which city did Peter meet girls ?" vs "in which city did Peter meet girls ?"
    "*about whom did they write stories ?" vs "for whom did they write stories ?"
    """
    places = (configs.Dirs.legal_words / 'name_of_place.txt').open().read().split()
    names = (configs.Dirs.legal_words / 'names.txt').open().read().split()
    pns = ["i", "you", "he", "she", "they"] 
    name_pns = names + pns
    vb_without_from_s = (configs.Dirs.legal_words / 'VB_not_go_with_from.txt').open().read().split()
    vb_with_for_s = (configs.Dirs.legal_words / 'VB_goes_with_for.txt').open().read().split()
    nouns_s_and_p = get_legal_words(tag='NN', second_tag='NNP')
    nouns_with_abaout_s = (configs.Dirs.legal_words / 'noun_followed_by_about.txt').open().read().split()
    while True:

            # random choices
            place = random.choice(places)
            name_pn = random.choice(name_pns)
            vb_without_from = random.choice(vb_without_from_s)
            vb_with_for = random.choice(vb_with_for_s)
            _, noun_pl = random.choice(nouns_s_and_p)
            nn_with_about = random.choice(nouns_with_abaout_s)

            # contrast is in number agreement between subject and copula
            yield template1['b'].format(place, name_pn, vb_without_from, noun_pl)  # bad
            yield template1['g'].format(place, name_pn, vb_without_from, noun_pl)  # good
            yield template2['b'].format(name_pn, vb_with_for, nn_with_about)  # bad
            yield template2['g'].format(name_pn, vb_with_for, nn_with_about)  # good

if __name__ == '__main__':
    for n, s in enumerate(collect_unique_pairs(main)):
        print(f'{n//2+1:>12,}', s)
