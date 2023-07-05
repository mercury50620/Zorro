from pathlib import Path
import collections
import nltk
from nltk.corpus import treebank, ptb, brown
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from zorro.words import get_legal_words

legal_words_path = Path("data/legal_words")
nltk.download('wordnet')
wnl = WordNetLemmatizer()

def flatten(l):#下のflatten_listに統合すべき
    for el in l:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def flatten_list(lst):
    if not isinstance(lst, list):
        return [lst]  # リスト以外の要素はそのまま返す

    result = []
    for item in lst:
        result.extend(flatten(item))  # 再帰的に要素を平坦化する
    return result

def find_pos_location(tree, pos): #-> list[tuple]
    positions = []
    for position in tree.treepositions():#深く見過ぎ
        if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos):
            positions.append(position)
    return positions

def find_word_location(tree, pos, word):#pos should be pos in a terminal node -> list[tuple]
    positions = []
    for position in tree.treepositions():
        if pos == "VB":
            if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos) and wnl.lemmatize(tree[position].leaves()[0], 'v') == word:
                positions.append(position)
        elif pos == "NN":
            if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos) and wnl.lemmatize(tree[position].leaves()[0], 'n') == word:
                positions.append(position)
        else:
            if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos) and tree[position].leaves()[0] == word:
                positions.append(position)
    return positions

def get_verbs_followed_by(tree, pos, prep):
    verbs_followed_by_prep = []
    prep_locs = find_word_location(tree, pos, prep)
    for pl in prep_locs:
        try:
            pos_location = find_pos_location(tree[pl[:-2]], "VB")
            pos_location = [pos_loc for pos_loc in pos_location if len(pos_loc) == 1]
            depended_pos_location = pos_location[0] #一つしか存在しないはずなので、便宜的に[0]で取ってきている
            verb = tree[pl[:-2]][depended_pos_location].leaves()[0] #一つしか存在しないはずなので、便宜的に[0]で取ってきている
            #print(tree[pl[:-2]])
            #print(verb)
            verbs_followed_by_prep.append(verb)
        except:
            pass
        return verbs_followed_by_prep

def get_nouns_followed_by(tree, pos, prep):
    nouns_followed_by_prep = []
    prep_locs = find_word_location(tree, pos, prep)
    for pl in prep_locs:
        try:
            if tree[pl[:-2]].label().startswith("NP"):
                pos_location = find_pos_location(tree[pl[:-2]], "NN")
                pos_location = [pos_loc for pos_loc in pos_location if len(pos_loc) == 2]
                depended_pos_location = pos_location[-1] #複数ある場合、最後がHEADになると思われるので[-1]で取ってきている
                noun = tree[pl[:-2]][depended_pos_location].leaves()[0]
                #print(tree[pl[:-2]])
                #print(noun)
                nouns_followed_by_prep.append(noun)
        except:
            pass
        return nouns_followed_by_prep

def get_object(tree, pred_pos, pred, obj_pos):
    objs = []
    pred_locs = find_word_location(tree, pred_pos, pred)
    for pl in pred_locs:
        try:
            pos_location = find_pos_location(tree[pl[:-1]], obj_pos)
            pos_location = [pos_loc for pos_loc in pos_location if len(pos_loc) == 1]
            for pos_loc in pos_location:
                obj = tree[pl[:-1]][pos_loc].leaves()[0] #一つしか存在しないはずなので、便宜的に[0]で取ってきている
                objs.append(obj)
            #print(tree[pl[:-2]])
            #print(verb)
        except:
            pass
        return objs

def get_verbs_in_ptb_cds(ptbw):
    cds_verbs = get_legal_words(tag='VB') + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBD')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBG')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBG')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBZ')]
    return list(set(ptbw) & set(cds_verbs))

def get_nouns_in_ptb_cds(ptbw):
    cds_nouns = get_legal_words(tag='NN')
    return list(set(ptbw) & set(cds_nouns))
'''
if __name__ == "__main__":
    
    articles = ptb.fileids()
    print(articles)


    verbs_followed_by_in = []
    for i, art in enumerate(articles[:20]):
        print((i / len(articles))* 100, '% 終了（verbs_followed_by_in）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            verbs_followed_by_in.append(get_verbs_followed_by(sents[i], "IN", 'in'))
    verbs_followed_by_in = flatten(verbs_followed_by_in)
    verbs_followed_by_in = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_in if x is not None]
    verbs_followed_by_in_freq = collections.Counter(verbs_followed_by_in)
    verbs_followed_by_in = [k for k, v in verbs_followed_by_in_freq.items() if v >= 3]
    verbs_followed_by_in_in_cds = get_verbs_in_ptb_cds(verbs_followed_by_in)

    
    with open(legal_words_path / "verbs_followed_by_in.txt", mode = 'w') as f:
        f.writelines('\n'.join(verbs_followed_by_in_in_cds))

    verbs_followed_by_from = []
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（verbs_followed_by_from）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            verbs_followed_by_from.append(get_verbs_followed_by(sents[i], "IN", 'from'))
        verbs_followed_by_from = flatten(verbs_followed_by_from)
        verbs_followed_by_from = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_from if x is not None] 
        verbs_followed_by_from_freq = collections.Counter(verbs_followed_by_from)

    verbs_followed_by_from = [k for k, v in verbs_followed_by_from_freq.items() if v >= 3]
    verbs_followed_by_from_in_cds = get_verbs_in_ptb_cds(verbs_followed_by_from)

    with open(legal_words_path / "verbs_followed_by_from.txt", mode = 'w') as f:
        f.writelines('\n'.join(verbs_followed_by_from_in_cds))

    #print(verbs_followed_by_in_not_by_from)
    #todo 他の者に関しても対応させ、トークン数を確認

    nouns_followed_by_from = []
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（nouns_followed_by_from）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            nouns_followed_by_from.append(get_nouns_followed_by(sents[i], "IN", 'from'))
        nouns_followed_by_from = flatten(nouns_followed_by_from)
        nouns_followed_by_from = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_from if x is not None]
        nouns_followed_by_from_freq = collections.Counter(nouns_followed_by_from)

    nouns_followed_by_from = [k for k, v in nouns_followed_by_from_freq.items() if v >= 3]
    nouns_followed_by_from_in_cds = get_nouns_in_ptb_cds(nouns_followed_by_from)
    
    with open(legal_words_path / "nouns_followed_by_from.txt", mode = 'w') as f:
        f.writelines('\n'.join(nouns_followed_by_from_in_cds))

    nouns_followed_by_in = []
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（nouns_followed_by_in）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            nouns_followed_by_in.append(get_nouns_followed_by(sents[i], "IN", 'in'))
        nouns_followed_by_in = flatten(nouns_followed_by_in)
        nouns_followed_by_in = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_in if x is not None]
        nouns_followed_by_in_freq = collections.Counter(nouns_followed_by_in)

    nouns_followed_by_in = [k for k, v in nouns_followed_by_in_freq.items() if v >= 3]
    nouns_followed_by_in_in_cds = get_nouns_in_ptb_cds(nouns_followed_by_in)
    
    with open(legal_words_path / "nouns_followed_by_in.txt", mode = 'w') as f:
        f.writelines('\n'.join(nouns_followed_by_in_in_cds))


    nouns_followed_by_to = []#toだけ少量のデータではなぜかうまくいかなかった
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（nouns_followed_by_to）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            nouns_followed_by_to.append(get_nouns_followed_by(sents[i], "IN", 'to'))
        nouns_followed_by_to = flatten(nouns_followed_by_to)
        nouns_followed_by_to = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_to if x is not None]
        nouns_followed_by_to_freq = collections.Counter(nouns_followed_by_to)

    nouns_followed_by_to = [k for k, v in nouns_followed_by_to_freq.items() if v >= 3]
    nouns_followed_by_to_in_cds = get_nouns_in_ptb_cds(nouns_followed_by_to)
    
    with open(legal_words_path / "nouns_followed_by_to.txt", mode = 'w') as f:
        f.writelines('\n'.join(nouns_followed_by_to_in_cds))

    nouns_followed_by_for = []
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（nouns_followed_by_for）')
        sents = ptb.parsed_sents(art)
        for i in range(len(sents)):
            nouns_followed_by_for.append(get_nouns_followed_by(sents[i], "IN", 'for'))
        nouns_followed_by_for = flatten(nouns_followed_by_for)
        nouns_followed_by_for = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_for if x is not None]
        nouns_followed_by_for_freq = collections.Counter(nouns_followed_by_for)

    nouns_followed_by_for = [k for k, v in nouns_followed_by_for_freq.items() if v >= 3]
    nouns_followed_by_for_in_cds = get_nouns_in_ptb_cds(nouns_followed_by_for)
    
    with open(legal_words_path / "nouns_followed_by_for.txt", mode = 'w') as f:
        f.writelines('\n'.join(nouns_followed_by_for_in_cds))
'''
if __name__ == "__main__":
    
    #nltk.download('ptb')
    articles = ptb.fileids()
    print(articles)
#動詞と目的語のペア
    verbs_nouns_pair = [] #->list[tuple(str, list[str, ...])]
    cds_verbs = set([wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBD')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBG')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBG')] + [wnl.lemmatize(v, 'v') for v in get_legal_words(tag='VBZ')])
    print(cds_verbs)
    for i, art in enumerate(articles):
        print((i / len(articles))* 100, '% 終了（verbs_nouns_pair）')
        sents = ptb.parsed_sents(art)
        for j in range(len(sents)):
            for v in cds_verbs:
                try:
                    verbs_nouns_pair.append((v, wnl.lemmatize(get_object(sents[j], "VB", v, "NN"), 'n')))
                    print(v)
                    print(get_object(sents, "VB", v, "NN"))
                except:
                    pass
    verbs_nouns_pair = flatten_list(verbs_nouns_pair)
    verbs_nouns_pair_freq = collections.Counter(verbs_nouns_pair)

    verbs_nouns_pair = [k for k, v in verbs_nouns_pair_freq.items() if v >= 3]
    verbs_nouns_pair_in_cds = get_nouns_in_ptb_cds(verbs_nouns_pair)

    with open(legal_words_path / "verbs_nouns_pair.txt", mode = 'w') as f:
        f.writelines('\n'.join(verbs_nouns_pair_in_cds))

    #print(verbs_followed_by_in_freq)
    #print(verbs_followed_by_from_freq)
    #print(nouns_followed_by_from_freq)
    #print(nouns_followed_by_in_freq)
    #print(nouns_followed_by_to_freq)
    #print(nouns_followed_by_for_freq)
    print(verbs_nouns_pair_freq)
