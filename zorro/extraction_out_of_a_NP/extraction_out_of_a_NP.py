import random
import inflect

from zorro.filter import collect_unique_pairs
from zorro.words import get_legal_words
from zorro.counterbalance import find_counterbalanced_subset
from zorro import configs
from zorro import make_verb_noun_dict

verb_noun_dict = make_verb_noun_dict()

#todo inflect使って目的語を複数形にする
pl = inflect.engine()
template1 = {
    'b': 'from which {place} did {name_pn} {vb_with_in} {noun_1} ?',
    'g': 'in which {place} did {name_pn} {vb_with_in} {noun_1} ?',
}

template2 = {
    'b': 'to which {human} did {name_pn} {vb_with_for} {noun_2} ?',
    'g': 'for which {human} did {name_pn} {vb_with_for} {noun_2} ?',
}



def main():
    """
    example:
    "*from which city did Peter meet girls ?" vs "in which city did Peter meet girls ?"
    "*to which customers did Mary retract boxes ?" vs "for which customers did Mary retract boxes ?"
    """
    places = (configs.Dirs.legal_words / 'name_of_place.txt').open().read().split()
    humans = (configs.Dirs.legal_words / 'humanity.txt').open().read().split()
    names = (configs.Dirs.legal_words / 'names.txt').open().read().split()
    pns = ["i", "you", "he", "she", "they"] 
    name_pns = names + pns
    vb_with_in_s = (configs.Dirs.legal_words / 'verbs_followed_by_in_but_not_by_from.txt').open().read().split()
    vb_with_for_s = (configs.Dirs.legal_words / 'verbs_followed_by_for_but_not_by_to.txt').open().read().split()
    nn_with_in_from = (configs.Dirs.legal_words / 'nouns_followed_by_from_and_by_in.txt').open().read().split()
    nn_with_to_for = (configs.Dirs.legal_words / 'nouns_followed_by_to_and_by_for.txt').open().read().split()

    while True:
        
        # random choices
        place = random.choice(places)
        human = random.choice(humans)
        name_pn = random.choice(name_pns)
        while True:    
            vb_with_in = random.choice(vb_with_in_s)
            if vb_with_in in verb_noun_dict:
                if len(set(verb_noun_dict[vb_with_in])&set(nn_with_in_from)) == 0:
                    #print('だめぽ')
                    continue
                while True:
                   noun_1_ = random.choice(verb_noun_dict[vb_with_in])
                   if noun_1_ in nn_with_in_from:
                       break
                break
        while True:
            vb_with_for = random.choice(vb_with_for_s)
            print(vb_with_for)
            if vb_with_for in verb_noun_dict:
                if len(set(verb_noun_dict[vb_with_for])&set(nn_with_to_for)) ==0:
                    #print('damepo')
                    continue
                while True:
                    noun_2_ = random.choice(verb_noun_dict[vb_with_for])
                    if noun_2_ in nn_with_to_for:
                        break
                break
        noun_1 = pl.plural(noun_1_)
        noun_2 = pl.plural(noun_2_)
        slot2filter = {
            'place': place,
            'human': human,
            'name_pn': name_pn,
            'vb_with_in':vb_with_in,
            'vb_with_for':vb_with_for,
            'noun_1':noun_1,
            'noun_2':noun_2
        }
        # contrast is in number agreement between subject and copula
        yield template1['b'].format(**slot2filter)  # bad
        yield template1['g'].format(**slot2filter)  # good
        yield template2['b'].format(**slot2filter)  # bad
        yield template2['g'].format(**slot2filter)  # good

if __name__ == '__main__':
    for n, s in enumerate(collect_unique_pairs(main)):
        print(f'{n//2+1:>12,}', s)
