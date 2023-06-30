import nltk
from nltk.corpus import treebank, ptb
from nltk.stem import WordNetLemmatizer

def find_pos_location(tree, pos): #-> list[tuple]
    positions = []
    for position in tree.treepositions():
        if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos):
            positions.append(position)
    return positions

def find_word_location(tree, pos, word):#pos should be pos in a terminal node -> list[tuple]
    positions = []
    for position in tree.treepositions():
        if isinstance(tree[position], nltk.tree.Tree) and tree[position].label().startswith(pos) and tree[position].leaves()[0] == word:
            positions.append(position)
    return positions

def get_verbs_followed_by(tree, pos, prep):
    verbs_followed_by_prep = []
    prep_locs = find_word_location(tree, pos, prep)
    for pl in prep_locs:
        #tree[pl[:-2] + find_pos_location(tree[pl[:-2]], "VB")]
        try:
            verb = tree[pl[:-2]][find_pos_location(tree[pl[:-2]], "VB")[0]].leaves()[0]
            verbs_followed_by_prep.append(verb)
        except:
            pass
    return verbs_followed_by_prep

nltk.download('treebank')
articles = treebank.fileids()

verbs_followed_by_in_not_by_from = []
for art in articles:
    sents = treebank.parsed_sents(art)
    for i in range(len(sents)):
        verbs_followed_by_in_not_by_from.append([get_verbs_followed_by(sents[i], "IN", 'in')])

print(verbs_followed_by_in_not_by_from)
#todo 他の者に関しても対応させ、トークン数を確認