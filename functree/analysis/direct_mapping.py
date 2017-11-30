import uuid, datetime, json
import pandas as pd
from functree import models


def from_table(form):
    raw_table = pd.read_csv(form.input_file.data, delimiter='\t', comment='#', header=0, index_col=0).dropna(how='all')
    profile = []
    for entry in raw_table.index:
        profile.append({'entry': entry, 'values': [raw_table.ix[entry].tolist()]})
    colors = []
    if form.color_file.data:
        colors = pd.read_csv(form.color_file.data, header=None, delimiter='\t').as_matrix().tolist()
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=profile,
        series=['Raw'],
        columns=[raw_table.columns.tolist()],
        colors=colors,
        target=form.target.data,
        description=form.description.data,
        added_at=datetime.datetime.utcnow(),
        private=form.private.data
    ).save().profile_id


def from_json(form):
    raw_data = json.load(form.input_file.data)
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=raw_data[0]['profile'],
        series=raw_data[0]['series'],
        columns=raw_data[0]['columns'],
        colors=raw_data[0]['colors'],
        target=form.target.data,
        description=form.description.data,
        added_at=datetime.datetime.utcnow(),
        private=form.private.data
    ).save().profile_id
