import sys, os, uuid, datetime, copy
import pandas as pd
from functree import models, tree, analysis

sys.path.append(os.path.join(os.path.dirname(__file__), '../crckm/src'))
import format_and_calculation as crckm


def from_table(form):
    result = calc_coverages(f=form.input_file.data, target=form.target.data)
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


def calc_coverages(f, target, method='mean'):
    root = models.Tree.objects().get(source=target)['tree']
    definition = models.Definition.objects().get(source=target)['definition']
    df = pd.read_csv(f, delimiter='\t', comment='#', header=0, index_col=0)

    root = copy.deepcopy(root)
    tree.delete_children(root, 'module')
    nodes = tree.get_nodes(root)
    graph = crckm.format_definition(definition)

    f.seek(0)
    df_crckm = crckm.calculate(ko_file=f, module_graphs=graph, method=method, threshold=0)

    results = {}
    analysis.calc_abundances(df_crckm, nodes, method, results)

    df_out = df.applymap(lambda x: int(bool(x))).append(results[method])    # Concatenate user's input and results

    profile = []
    for entry in df_out.index:
        values = [df_out.ix[entry].tolist()]
        profile.append({'entry': entry, 'values': values})
    data = {
        'profile': profile,
        'series': ['Module coverage'],
        'columns': [df_out.columns.tolist()]
    }
    return data
