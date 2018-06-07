import uuid, datetime
import pandas as pd, numpy as np, scipy.stats
from functree import app, models, tree, analysis


def from_table(form):
    result = calc_abundances(f1=form.input_file1.data, f2=form.input_file2.data, target=form.target.data)
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


def calc_abundances(f1, f2, target):
    df1 = pd.read_csv(f1, delimiter='\t', comment='#', header=0, index_col=0)
    df2 = pd.read_csv(f2, delimiter='\t', comment='#', header=0, index_col=0)
    root = models.Tree.objects().get(source=target)['tree']
    nodes = tree.get_nodes(root)
    entry_to_layer = dict(map(lambda x: (x['entry'], x['layer']), nodes))

    # transform external annotations to kegg KOs
    if target.lower() in ["kegg", "foam", "enteropathway"]:
        df1 = analysis.map_external_annotations(df1)
        df2 = analysis.map_external_annotations(df2)

    results1 = {}
    analysis.calc_abundances(df1, nodes, 'mean', results1)
    results2 = {}
    analysis.calc_abundances(df2, nodes, 'mean', results2)

    df_result = pd.DataFrame()
    for entry in (set(results1['mean'].index) & set(results2['mean'].index)):
        try:
            result = scipy.stats.mannwhitneyu(results1['mean'].loc[entry], results2['mean'].loc[entry])
        except ValueError:
            pass
        else:
            pvalue = result.pvalue
            if pvalue < 0.05:
                score = -np.log10(result.pvalue)
            else:
                score = 0
            df_result.loc[entry, 'P-value'] = pvalue
            df_result.loc[entry, 'Score'] = score

    profile = []
    for entry in df_result.index:
        values = [df_result.ix[entry].tolist()]
        profile.append({'entry': entry, 'layer': analysis.get_layer(entry, entry_to_layer), 'values': values})

    data = {
        'profile': profile,
        'series': ['Mann-Whitney U test'],
        'columns': [['P-value', 'Score']]
    }
    return data
