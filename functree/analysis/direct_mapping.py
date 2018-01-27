import uuid, datetime, json
import pandas as pd
from functree import app, models, tree, analysis


def from_table(form):
    raw_table = pd.read_csv(form.input_file.data, delimiter='\t', comment='#', header=0, index_col=0).dropna(how='all')
    root = models.Tree.objects().get(source=form.target.data)['tree']
    nodes = tree.get_nodes(root)
    entry_to_layer = dict(map(lambda x: (x['entry'], x['layer']), nodes))

    profile = []
    for entry in raw_table.index:
        profile.append({'entry': entry, 'layer': analysis.get_layer(entry, entry_to_layer), 'values': [raw_table.ix[entry].tolist()]})
    colors = []
    if form.color_file.data:
        colors = pd.read_csv(form.color_file.data, header=None, delimiter='\t').as_matrix().tolist()
    utcnow = datetime.datetime.utcnow()
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=profile,
        series=['Raw'],
        columns=[raw_table.columns.tolist()],
        colors=colors,
        target=form.target.data,
        description=form.description.data,
        added_at=utcnow,
        expire_at=utcnow + datetime.timedelta(days=app.config['FUNCTREE_PROFILE_TTL_DAYS']),
        private=form.private.data
    ).save().profile_id


def from_json(form):
    raw_data = json.load(form.input_file.data)
    utcnow = datetime.datetime.utcnow()
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=raw_data[0]['profile'],
        series=raw_data[0]['series'],
        columns=raw_data[0]['columns'],
        colors=raw_data[0]['colors'],
        target=form.target.data,
        description=form.description.data,
        added_at=utcnow,
        expire_at=utcnow + datetime.timedelta(days=app.config['FUNCTREE_PROFILE_TTL_DAYS']),
        private=form.private.data
    ).save().profile_id
