from functree import db


class Tree(db.Document):
    tree = db.DictField(required=True)
    source = db.StringField(required=True)
    description = db.StringField(required=True, max_length=50)
    added_at = db.DateTimeField(required=True)


class Definition(db.Document):
    definition = db.DictField(default={})
    source = db.StringField(required=True, choices=[])
    description = db.StringField(required=True, max_length=50)
    added_at = db.DateTimeField(required=True)


class Profile(db.Document):
    profile_id = db.UUIDField(binary=True, required=True, unique=True)
    profile = db.ListField(default=[])
    series = db.ListField(default=[])
    columns = db.ListField(default=[])
    colors = db.ListField(default=[])
    target = db.StringField(required=True, choices=[])
    description = db.StringField(max_length=50)
    added_at = db.DateTimeField(required=True)
    expire_at = db.DateTimeField(required=True)
    private = db.BooleanField(default=True)
    locked = db.BooleanField(default=False)
    meta = {
        'indexes': [
            {'fields': ['expire_at'], 'expireAfterSeconds': 0}
        ]
    }

class AnnotationMapping(db.Document):
    annotation = db.StringField(required=True, max_length=100)
    ko_map = db.ListField(default=[])
