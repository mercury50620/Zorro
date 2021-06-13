"""
compare accuracy between models saved in local or remote runs folder, at one time step.
"""
from collections import defaultdict
from typing import List, Optional
import numpy as np

from zorro import configs
from zorro.visualizer import VisualizerBars, ParadigmDataBars
from zorro.utils import prepare_data_for_plotting, get_phenomena_and_paradigms
from zorro.utils import load_group_names, get_legend_label
from zorro.io import get_group2model_output_paths


STEP = '*'
IS_LOCAL = True
REP = 0
PARAM_NAMES: Optional[List[str]] = None  # [f'param_{i:03}' for i in [1, 2]]
CONDITIONS = ['leave_unmasked_prob', ]

if IS_LOCAL:
    configs.Eval.local_runs = True
else:
    configs.Eval.local_runs = False

group_names = load_group_names(PARAM_NAMES)
labels = [get_legend_label(gn, conditions=CONDITIONS, add_data_size=True)
          for gn in group_names]

# get list of (phenomenon, paradigm) tuples
phenomena_paradigms = get_phenomena_and_paradigms()

# collects and plots each ParadigmData instance in 1 multi-axis figure
v = VisualizerBars(phenomena_paradigms=phenomena_paradigms)

# for all paradigms
for n, (phenomenon, paradigm) in enumerate(phenomena_paradigms):
    print(f'Scoring and plotting results for phenomenon={phenomenon:<36} paradigm={paradigm:<36} '
          f'{n + 1:>2}/{len(phenomena_paradigms)}')

    # load model output at all available steps
    group_name2model_output_paths_ = get_group2model_output_paths(group_names,
                                                                  phenomenon,
                                                                  paradigm,
                                                                  step=STEP,
                                                                  )
    # make sure there is only one rep per group name so that averaging works correctly
    group_name2model_output_paths = {}
    for gn, paths in group_name2model_output_paths_.items():
        paths = [path for path in paths if 'excluded' not in str(path)]
        if not len(paths) == 1:
            raise RuntimeError(f'Found {len(paths)} output files for {gn}:\n{[str(p) for p in paths]}.'
                               f'Add "excluded" to folder name to exclude individual reps.')
        else:
            group_name2model_output_paths[gn] = paths

    # init data
    group_name2template2acc = defaultdict(dict)
    group_name2rep2acc = defaultdict(dict)

    # calc + collect accuracy
    template2group_name2accuracies = prepare_data_for_plotting(group_name2model_output_paths,
                                                               phenomenon,
                                                               paradigm,
                                                               )

    # collect average performance in each paradigm, grouped by replication - allows computation of statistics
    for group_name, accuracies in template2group_name2accuracies['all templates'].items():
        for rep, acc in enumerate(accuracies):
            group_name2rep2acc[group_name][rep] = acc  # collapsed over templates

    # collect average performance in each paradigm, grouped by template
    for template, group_name2accuracies in template2group_name2accuracies.items():
        if template == 'all templates':
            continue
        for group_name, accuracies in group_name2accuracies.items():
            acc_avg_over_reps = np.mean(accuracies)  # average over reps
            group_name2template2acc[group_name][template] = acc_avg_over_reps

    pd = ParadigmDataBars(
        phenomenon=phenomenon,
        paradigm=paradigm,
        group_names=group_names,
        labels=labels,
        group_name2template2acc=group_name2template2acc,
        group_name2rep2acc=group_name2rep2acc,
    )

    # plot each paradigm in separate axis
    v.update(pd)

v.plot_summary()
