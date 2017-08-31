from functree import db


class Tree(db.Document):
    tree = db.DictField()
    source = db.StringField()
    description = db.StringField()
    added_at = db.DateTimeField()


class Profile(db.Document):
    __tree_sources = Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    profile_id = db.StringField()
    profile = db.ListField(default=[])
    series = db.ListField(default=[])
    columns = db.ListField(default=[])
    target = db.StringField(choices=[
        tree_source['_id'] for tree_source in __tree_sources
    ])
    description = db.StringField(max_length=50)
    added_at = db.DateTimeField()
    private = db.BooleanField(default=False)


class Definition(db.Document):
    __tree_sources = Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    definition = db.DictField()
    source = db.StringField(choices=[
        tree_source['_id'] for tree_source in __tree_sources
    ])
    description = db.StringField()
    added_at = db.DateTimeField()
