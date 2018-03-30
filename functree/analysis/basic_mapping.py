import uuid, datetime, multiprocessing
import pandas as pd
from functree import app, models, tree, analysis


def from_table(form):
    methods=['mean', 'sum']
    if form.modulecoverage.data:
        methods.append('modulecoverage')
    result = calc_abundances(f=form.input_file.data, target=form.target.data, methods=methods)
    colors = []
    if form.color_file.data:
        colors = pd.read_csv(form.color_file.data, header=None, delimiter='\t').as_matrix().tolist()
    utcnow = datetime.datetime.utcnow()
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=result['profile'],
        series=result['series'],
        columns=result['columns'],
        colors=colors,
        target=form.target.data,
        description=form.description.data,
        added_at=utcnow,
        expire_at=utcnow + datetime.timedelta(days=app.config['FUNCTREE_PROFILE_TTL_DAYS']),
        private=form.private.data
    ).save().profile_id


def calc_abundances(f, target, methods):
    df = pd.read_csv(f, delimiter='\t', comment='#', header=0, index_col=0)
    root = models.Tree.objects().get(source=target)['tree']
    nodes = tree.get_nodes(root)
    entry_to_layer = dict(map(lambda x: (x['entry'], x['layer']), nodes))

    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    jobs = list()
    for method in methods:
        if not method == "modulecoverage":
            job = multiprocessing.Process(target=analysis.calc_abundances, args=(df, nodes, method, shared_data), daemon=False)
        else:
            # Point back to the beginning of the file
            f.seek(0)
            job = multiprocessing.Process(target=analysis.module_coverage.calc_coverages, args=(f, target, shared_data), daemon=False)
        job.start()
        jobs.append(job)
    for job in jobs:
        job.join()
    results = dict(shared_data)

    profile = []
    # load KO based entries
    entries=list(list(results.values())[0].index)
    if "modulecoverage" in methods:
        entries += list(list(results.values())[2].index)
        entries = list(set(entries))

    for entry in entries:
        #values = [results[method].ix[entry].tolist() for method in methods]
        values = []
        for method in methods:
            if entry in results[method].index:
                values.append(results[method].ix[entry].tolist())
            else:
                values.append([0] * df.columns.size)
        profile.append({'entry': entry, 'layer': analysis.get_layer(entry, entry_to_layer), 'values': values})
    data = {
        'profile': profile,
        'series': methods,
        'columns': [df.columns.tolist() for i in range(len(methods))]
    }
    return data
