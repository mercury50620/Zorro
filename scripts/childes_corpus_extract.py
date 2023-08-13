from typing import List
from pathlib import Path
import glob
from nltk.tree import Tree
import nltk
from nltk.stem import WordNetLemmatizer
from zorro import configs
from zorro.words import get_legal_words
import collections

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
    for position in tree.treepositions():#深く見過ぎ todo 一個下までしか見ない関数に変更 -> search_pos_locationに置き換えられるべき
        if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos):
            positions.append(position)
    return positions

def search_pos_location(tree, pos): #treeの一個下までしか見ない 一個しかとってこれない
    if pos != "NN" and pos != "VB" and pos != "JJ":
        raise ValueError("対応していない品詞です")

    for position in tree.treepositions():
        if len(position) != 1:
            pass
        elif tree[position].label().startswith(pos[0] + "P"):

            return tuple(list(position) + list(search_pos_location(tree[position], pos)))
        elif tree[position].label().startswith(pos):
            return position
        else:
            pass

def find_word_location(tree, pos, word) -> List[tuple]:#pos should be pos in a terminal node -> list[tuple]
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
                nouns_followed_by_prep.append(noun)
        except:
            pass
        return nouns_followed_by_prep

def get_object(tree, pred_pos, pred, obj_pos) -> list:
    objs = []
    pred_locs = find_word_location(tree, pred_pos, pred)
    for pl in pred_locs:
        pos_location = search_pos_location(tree[pl[:-1]], obj_pos)
        #print(tree[pl[:-1]])
        #print(pos_location, "pos_location")
        #print(tree[pl[:-1]][pos_location].leaves())
        obj = tree[pl[:-1]][pos_location].leaves()[0] #一つしか存在しないはずなので、便宜的に[0]で取ってきている
        objs.append(obj)
        return objs


directory_path = configs.Dirs.childes_treebank
pattern = '**/*.parsed'

childes_trees = glob.glob(str(configs.Dirs.childes_treebank / pattern), recursive = True)



def split_trees(trees:str) -> List[str]:
    lines = trees.split('\n')
    result = []
    current_block = []

    for line in lines:
        if line.strip() == '':
            if current_block:
                result.append('\n'.join(current_block))
                current_block = []
        else:
            current_block.append(line)

    if current_block:
        result.append('\n'.join(current_block))

    return result

if __name__ == "__main__":
    sents = []
    for tree_path in childes_trees:
        with open (tree_path) as f:
            trees = f.read()
            raw_trees = split_trees(trees)
            for i, rt in enumerate(raw_trees):
                try:
                    sents.append(Tree.fromstring(rt))
                except:
                    pass


    cds_verbs = (configs.Dirs.legal_words / 'legal_verbs.txt').open().read().split()
    cds_nouns = (configs.Dirs.legal_words / 'legal_nouns.txt').open().read().split()
    cds_adjectives = (configs.Dirs.legal_words / 'legal_adjectives.txt').open().read().split()

    verbs_followed_by_in = []
    verbs_followed_by_from = []
    verbs_followed_by_for = []
    verbs_followed_by_to = []
    nouns_followed_by_from = []
    nouns_followed_by_in = []
    nouns_followed_by_to = []
    nouns_followed_by_for = []
    
    verbs_nouns_pair = [] #->list[tuple(str, list[str, ...])]
    nouns_adj_pair = []



    for i in range(len(sents)):
        print((i / len(sents))* 100, '% 終了')
        verbs_followed_by_in.append(get_verbs_followed_by(sents[i], "IN", 'in'))
        verbs_followed_by_from.append(get_verbs_followed_by(sents[i], "IN", 'from'))
        verbs_followed_by_for.append(get_verbs_followed_by(sents[i], "IN", 'for'))
        verbs_followed_by_to.append(get_verbs_followed_by(sents[i], "IN", 'to'))
        nouns_followed_by_from.append(get_nouns_followed_by(sents[i], "IN", 'from'))
        nouns_followed_by_from.append(get_nouns_followed_by(sents[i], "IN", 'in'))
        nouns_followed_by_to.append(get_nouns_followed_by(sents[i], "IN", 'to'))
        nouns_followed_by_for.append(get_nouns_followed_by(sents[i], "IN", 'for'))
        for v in cds_verbs:
            try:
                for obj in get_object(sents[i], "VB", v, "NN"):

                    verbs_nouns_pair.append((v, wnl.lemmatize(obj, 'n')))      
            except:
                pass
        
        for adj in cds_adjectives:
            try:
                for n in get_object(sents[i], "JJ", adj, "NN"):
                    nouns_adj_pair.append((n, adj))
            except:
                pass
    #verb_followed_by_in
    verbs_followed_by_in = flatten(verbs_followed_by_in)
    verbs_followed_by_in = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_in if x is not None]
    verbs_followed_by_in_freq = collections.Counter(verbs_followed_by_in)
    verbs_followed_by_in = [k for k, v in verbs_followed_by_in_freq.items() if v >= 3]
    verbs_followed_by_in_in_cds = set([v for v in verbs_followed_by_in if v in cds_verbs])
    print(verbs_followed_by_in_in_cds)
    #with open(legal_words_path / "verbs_followed_by_in.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_in_in_cds))
    
    #verb_followed_by_from
    verbs_followed_by_from = flatten(verbs_followed_by_from)
    verbs_followed_by_from = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_from if x is not None] 
    verbs_followed_by_from = set(verbs_followed_by_from) 

    #with open(legal_words_path / "verbs_followed_by_from.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_from_in_cds))

    #verbs_followed_by_in_but_not_by_from
    verbs_followed_by_in_but_not_by_from = list(verbs_followed_by_in_in_cds - verbs_followed_by_from)
    #with open(legal_words_path / "verbs_followed_by_in_but_not_by_from.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_in_but_not_by_from))
    
    #verb_followed_by_for
    verbs_followed_by_for = flatten(verbs_followed_by_for)
    verbs_followed_by_for = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_for if x is not None] 
    verbs_followed_by_for_freq = collections.Counter(verbs_followed_by_for)
    verbs_followed_by_for = [k for k, v in verbs_followed_by_for_freq.items() if v >= 3]
    verbs_followed_by_for_in_cds = set([v for v in verbs_followed_by_for if v in cds_verbs])
    print(verbs_followed_by_for_in_cds)
    #with open(legal_words_path / "verbs_followed_by_for.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_for_in_cds))    
    
    #verb_followed_by_to
    verbs_followed_by_to = flatten(verbs_followed_by_to)
    verbs_followed_by_to = [wnl.lemmatize(x, 'v') for x in verbs_followed_by_to if x is not None] 
    verbs_followed_by_to = set(verbs_followed_by_to)
    #with open(legal_words_path / "verbs_followed_by_to.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_to_in_cds))    

    #verbs_followed_by_for_but_not_by_to
    verbs_followed_by_for_but_not_by_to = list(verbs_followed_by_for_in_cds - verbs_followed_by_to)
    #with open(legal_words_path / "verbs_followed_by_for_but_not_by_to.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(verbs_followed_by_for_but_not_by_to))

    #nouns_followed_by_from
    nouns_followed_by_from = flatten(nouns_followed_by_from)
    nouns_followed_by_from = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_from if x is not None]
    nouns_followed_by_from_freq = collections.Counter(nouns_followed_by_from)
    nouns_followed_by_from = [k for k, v in nouns_followed_by_from_freq.items() if v >= 3]
    nouns_followed_by_from_in_cds = [n for n in nouns_followed_by_from if n in cds_nouns]
    print(nouns_followed_by_from_in_cds)
    #with open(legal_words_path / "nouns_followed_by_from.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(nouns_followed_by_from_in_cds))

    #nouns_followed_by_in
    nouns_followed_by_in = flatten(nouns_followed_by_in)
    nouns_followed_by_in = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_in if x is not None]
    nouns_followed_by_in_freq = collections.Counter(nouns_followed_by_in)
    nouns_followed_by_in = [k for k, v in nouns_followed_by_in_freq.items() if v >= 3]
    nouns_followed_by_in_in_cds = [n for n in nouns_followed_by_in if n in cds_nouns]
    print(nouns_followed_by_in_in_cds)
    #with open(legal_words_path / "nouns_followed_by_in.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(nouns_followed_by_in_in_cds))

    #nouns_followed_by_from_and_by_in
    nouns_followed_by_from_and_by_in = set(nouns_followed_by_from_in_cds)&set(nouns_followed_by_in_in_cds)
    #with open(legal_words_path / "nouns_followed_by_from_and_by_in.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(list(nouns_followed_by_from_and_by_in)))

    #nouns_followed_by_to
    nouns_followed_by_to = flatten(nouns_followed_by_to)
    nouns_followed_by_to = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_to if x is not None]
    nouns_followed_by_to_freq = collections.Counter(nouns_followed_by_to)
    nouns_followed_by_to = [k for k, v in nouns_followed_by_to_freq.items() if v >= 3]
    nouns_followed_by_to_in_cds = [n for n in nouns_followed_by_to if n in cds_nouns]
    print(nouns_followed_by_to_in_cds)
    #with open(legal_words_path / "nouns_followed_by_to.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(nouns_followed_by_to_in_cds))
    
    #nouns_followed_by_for
    nouns_followed_by_for = flatten(nouns_followed_by_for)
    nouns_followed_by_for = [wnl.lemmatize(x, 'n') for x in nouns_followed_by_for if x is not None]
    nouns_followed_by_for_freq = collections.Counter(nouns_followed_by_for)
    nouns_followed_by_for = [k for k, v in nouns_followed_by_for_freq.items() if v >= 3]
    nouns_followed_by_for_in_cds = [n for n in nouns_followed_by_for if n in cds_nouns]
    print(nouns_followed_by_for_in_cds)
    #with open(legal_words_path / "nouns_followed_by_for.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(nouns_followed_by_for_in_cds))

    #nouns_followed_by_to_and_by_for
    nouns_followed_by_to_and_by_for = set(nouns_followed_by_to_in_cds)&set(nouns_followed_by_for_in_cds)
    #with open(legal_words_path / "nouns_followed_by_to_and_by_for.txt", mode = 'w') as f:
    #    f.writelines('\n'.join(nouns_followed_by_to_and_by_for))

    #verbs_nouns_pair
    verbs_nouns_pair_freq = collections.Counter(verbs_nouns_pair)
    verbs_nouns_pair = [k for k, v in verbs_nouns_pair_freq.items() if v >= 2]
    verbs_nouns_pair_in_cds = [(v,n) for v, n in verbs_nouns_pair if v in cds_verbs and n in cds_nouns] 
    print(verbs_nouns_pair_in_cds)

    #with open(legal_words_path / "verbs_nouns_pair.txt", mode = 'w') as f:
    #    for vn_pair in verbs_nouns_pair_in_cds:
    #        line = f"{vn_pair[0]}, {vn_pair[1]}\n"
    #        f.write(line)

    print(verbs_nouns_pair_freq)

    #nouns_adj_pair
    nouns_adj_pair_freq = collections.Counter(nouns_adj_pair)
    nouns_adj_pair = [k for k, v in nouns_adj_pair_freq.items() if v >= 2]
    nouns_adj_pair_in_cds = [(n,a) for n, a in nouns_adj_pair if n in cds_nouns and a in cds_adjectives] 
    print(nouns_adj_pair_in_cds)

    with open(legal_words_path / "nouns_adj_pair_in_cds.txt", mode = 'w') as f:
        for na_pair in nouns_adj_pair_in_cds:
            line = f"{na_pair[0]}, {na_pair[1]}\n"
            f.write(line)

    print(nouns_adj_pair_freq)
