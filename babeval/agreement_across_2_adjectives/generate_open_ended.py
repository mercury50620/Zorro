
from babeval import configs
from babeval.agreement_across_2_adjectives.shared import task_name, pre_nominals_singular, pre_nominals_plural
from babeval.task_words import get_task_word_combo

NUM_ADJECTIVES = 2

template1 = 'look at {} {} {}' + f' {configs.Data.mask_symbol} ' + '.'
template2 = '{} {} {}' + f' {configs.Data.mask_symbol} ' + 'went there .'


def main():
    """
    example:
    "look at this green [MASK] .
    "these green [MASK] went there .
    """

    for pre_nominal in pre_nominals_singular + pre_nominals_plural:

        for words in get_task_word_combo(task_name, (('JJ', 0, NUM_ADJECTIVES),
                                                     ('JJ', 1, NUM_ADJECTIVES),)):
            yield template1.format(pre_nominal, *words)
            yield template2.format(pre_nominal, *words)


if __name__ == '__main__':
    for s in main():
        print(s)