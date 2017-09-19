from functree import db


class Tree(db.Document):
    tree = db.DictField(required=True)
    source = db.StringField(required=True)
    description = db.StringField(required=True, max_length=50)
    added_at = db.DateTimeField(required=True)


class Profile(db.Document):
    _tree_sources = Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    profile_id = db.UUIDField(binary=True, required=True, unique=True)
    profile = db.ListField(default=[])
    series = db.ListField(default=[])
    columns = db.ListField(default=[])
    target = db.StringField(required=True, choices=[
        tree_source['_id'] for tree_source in _tree_sources
    ])
    description = db.StringField(required=True, max_length=50)
    added_at = db.DateTimeField(required=True)
    private = db.BooleanField(default=False)


class Definition(db.Document):
    _tree_sources = Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    definition = db.DictField(default={})
    source = db.StringField(required=True, choices=[
        tree_source['_id'] for tree_source in _tree_sources
    ])
    description = db.StringField(required=True, max_length=50)
    added_at = db.DateTimeField(required=True)
