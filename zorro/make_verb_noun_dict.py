from zorro import configs

def make_verb_noun_dict():
    values = []
    lines_list = (configs.Dirs.legal_words / 'verbs_nouns_pair.txt').open().read().split('\n')
    verb_noun_dict = {}
    for l in lines_list:
        verb, noun = l.split(", ")
        if verb in verb_noun_dict:
            verb_noun_dict[verb].append(noun)
            values.append(noun)
        else:
            verb_noun_dict[verb] = [noun]
            values.append(noun)
        #print(verb_noun_dict.keys())
    return verb_noun_dict

def make_adj_noun_dict():
    lines_list = (configs.Dirs.legal_words / 'nouns_adj_pair_in_cds.txt').open().read().split('\n')
    adj_noun_dict = {}
    for l in lines_list:
        noun, adj = l.split(", ")
        if adj in adj_noun_dict:
            adj_noun_dict[adj].append(noun)
        else:
            adj_noun_dict[adj] = [noun]
    return adj_noun_dict

def make_bare_past_dict():
    return {'get':'got',
     'read':'read',
     'like':'liked',
     'make':'made',
     'turn':'turned',
     'watch':'watched',
     'take':'took',
     'open':'opened',
     'need':'needed',
     'see':'saw',
     'use':'used',
     'send':'sent',
     'lose':'lost',
     'break':'broke',
     'know':'knew',
     'show':'showed',
     'win':'won',
     'look':'looked',
     'cost':'cost',
     'help':'helped',
     'meet':'met',
     'mean':'meant'}