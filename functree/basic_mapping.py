import uuid, datetime
from functree import models, analysis


def from_table(form):
    result = analysis.perform_basic(f=form.input_file.data, target=form.target.data)
    return models.Profile(
        profile_id=uuid.uuid4(),
        profile=result['profile'],
        series=result['series'],
        columns=result['columns'],
        target=form.target.data,
        description=form.description.data,
        added_at=datetime.datetime.utcnow(),
        private=form.private.data
    ).save().profile_id
