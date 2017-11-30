import uuid, datetime, multiprocessing
import pandas as pd
from functree import models, tree, analysis


def from_table(form):
    result = calc_abundances(f=form.input_file.data, target=form.target.data)
    colors = []
    if form.color_file.data:
        colors = pd.read_csv(form.color_file.data, header=None, delimiter='\t').as_matrix().tolist()
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=result['profile'],
        series=result['series'],
        columns=result['columns'],
        colors=colors,
        target=form.target.data,
        description=form.description.data,
        added_at=datetime.datetime.utcnow(),
        private=form.private.data
    ).save().profile_id


def calc_abundances(f, target, methods=['sum', 'mean']):
    df = pd.read_csv(f, delimiter='\t', comment='#', header=0, index_col=0)
    root = models.Tree.objects().get(source=target)['tree']
    nodes = tree.get_nodes(root)

    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    jobs = list()
    for method in methods:
        job = multiprocessing.Process(target=analysis.calc_abundances, args=(df, nodes, method, shared_data), daemon=False)
        job.start()
        jobs.append(job)
    for job in jobs:
        job.join()
    results = dict(shared_data)

    profile = []
    for entry in list(results.values())[0].index:
        values = [results[method].ix[entry].tolist() for method in methods]
        profile.append({'entry': entry, 'values': values})
    data = {
        'profile': profile,
        'series': methods,
        'columns': [df.columns.tolist() for i in range(len(methods))]
    }
    return data
