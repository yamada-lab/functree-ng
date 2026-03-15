import uuid as _uuid
import setuptools_scm, flask, flask_mongoengine, flask_wtf.csrf, flask_httpauth, flask_caching, flask_debugtoolbar
from bson import json_util as _bson_json_util
from bson.codec_options import UuidRepresentation as _UuidRepr
import mongoengine.base as _me_base

__version__ = setuptools_scm.get_version(root='..', relative_to=__file__)

app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_object('functree.config')
app.config.from_pyfile('config.py', silent=True)

db = flask_mongoengine.MongoEngine(app)
csrf = flask_wtf.csrf.CSRFProtect(app)
auth = flask_httpauth.HTTPDigestAuth()
cache = flask_caching.Cache(app)
toolbar = flask_debugtoolbar.DebugToolbarExtension(app)

app.session_interface = flask_mongoengine.MongoEngineSessionInterface(db)

# pymongo 4.x: bson.json_util._json_convert() uses UuidRepresentation.UNSPECIFIED by default,
# which refuses to encode native uuid.UUID objects (e.g. from UUIDField(binary=True)).
# Override the document encoding path to pass UuidRepresentation.STANDARD so UUIDs are
# serialised as {"$uuid": "..."} extended JSON strings.
_UUID_JSON_OPTS = _bson_json_util.JSONOptions(uuid_representation=_UuidRepr.STANDARD)

class _JSONEncoder(app.json_encoder):
    def default(self, obj):
        if isinstance(obj, _me_base.BaseDocument):
            return _bson_json_util._json_convert(obj.to_mongo(), json_options=_UUID_JSON_OPTS)
        if isinstance(obj, _uuid.UUID):
            return str(obj)
        return super().default(obj)

app.json_encoder = _JSONEncoder

import functree.views
