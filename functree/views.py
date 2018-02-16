import datetime, json, os, uuid, urllib.request, urllib.error, re
import flask, werkzeug.exceptions, cairosvg
from functree import __version__, app, auth, filters, forms, models, tree, analysis, cache
from functree.crckm.src import download as crckm


@app.route('/')
def route_index():
    return flask.render_template('index.html')


@app.route('/analysis/<string:mode>/', methods=['GET', 'POST'])
def route_analysis(mode):
    if mode == 'mapping':
        form = forms.MappingForm()
        if form.validate_on_submit():
            profile_id = analysis.basic_mapping.from_table(form)
            return flask.redirect(flask.url_for('route_viewer') + '?profile_id={}'.format(profile_id))
        else:
            return flask.render_template('mapping.html', form=form, mode=mode)
    elif mode == 'comparison':
        form = forms.ComparisonForm()
        if form.validate_on_submit():
            profile_id = analysis.comparison.from_table(form)
            return flask.redirect(flask.url_for('route_viewer') + '?profile_id={}'.format(profile_id))
        else:
            return flask.render_template('analysis.html', form=form, mode=mode)
    elif mode == 'direct_mapping':
        form = forms.DirectMappingForm()
        if form.validate_on_submit():
            profile_id = analysis.direct_mapping.from_table(form)
            return flask.redirect(flask.url_for('route_viewer') + '?profile_id={}'.format(profile_id))
        else:
            return flask.render_template('analysis.html', form=form, mode=mode)
    elif mode == 'json_upload':
        form = forms.JSONUploadForm()
        if form.validate_on_submit():
            profile_id = analysis.direct_mapping.from_json(form)
            return flask.redirect(flask.url_for('route_viewer') + '?profile_id={}'.format(profile_id))
        else:
            return flask.render_template('analysis.html', form=form, mode=mode)
    else:
        flask.abort(404)


@app.route('/list/')
def route_list():
    only = ('profile_id', 'description', 'added_at', 'target', 'locked')
    profiles = models.Profile.objects().filter(private=False).only(*only)
    return flask.render_template('list.html', profiles=profiles)


@app.route('/data/')
def route_data():
    only = ('source', 'description', 'added_at')
    trees = models.Tree.objects().all().only(*only)
    definitions = models.Definition.objects().all().only(*only)
    return flask.render_template('data.html', trees=trees, definitions=definitions)


@app.route('/docs/', defaults={'filename': 'index.html'})
@app.route('/docs/<path:filename>')
def route_docs(filename):
    return flask.render_template('help.html')


@app.route('/about/')
def route_about():
    return flask.render_template('about.html', version=__version__)


@app.route('/contact/')
def route_contact():
    return flask.render_template('contact.html')


@app.route('/viewer/')
def route_viewer():
    profile_id = flask.request.args.get('profile_id', type=uuid.UUID)
    mode = flask.request.args.get('mode', default='functree', type=str)
    excludes = ('profile',)
    profile = models.Profile.objects().exclude(*excludes).get_or_404(profile_id=profile_id)
    if mode == 'functree':
        root = flask.request.args.get('root', type=str)
        return flask.render_template('functree.html', profile=profile, mode=mode, root=root)
    elif mode == 'charts':
        series = flask.request.args.get('series', default=0, type=int)
        return flask.render_template('charts.html', profile=profile, mode=mode, series=series)
    elif mode == 'pathways':
        series = flask.request.args.get('series', default=0, type=int)
        return flask.render_template('pathways.html', profile=profile, mode=mode, series=series)
    elif mode == 'tables':
        series = flask.request.args.get('series', default=0, type=int)
        return flask.render_template('tables.html', profile=profile, mode=mode, series=series)
    elif mode == 'summary':
        return flask.render_template('summary.html', profile=profile, mode=mode)
    else:
        flask.abort(404)


@app.route('/admin/')
@auth.login_required
def route_admin():
    counts = {
        'profile': models.Profile.objects().count(),
        'tree': models.Tree.objects().count(),
        'definition': models.Definition.objects().count()
    }
    return flask.render_template('admin.html', counts=counts)


@app.route('/profile/<uuid:profile_id>', methods=['GET'])
@cache.cached()
def route_profile(profile_id):
    excludes = ('id',)
    profile = models.Profile.objects.exclude(*excludes).get_or_404(profile_id=profile_id)
    return flask.jsonify([profile])


@app.route('/profile/<uuid:profile_id>', methods=['POST'])
def route_profile_delete(profile_id):
    if flask.request.form.get('_method') == 'DELETE':
        models.Profile.objects.get_or_404(profile_id=profile_id, locked=False).delete()
        return flask.redirect(flask.url_for('route_list'))
    else:
        return flask.abort(405)


@app.route('/tree/<string:source>')
@cache.cached()
def route_tree(source):
    excludes = ('id',)
    tree = models.Tree.objects().exclude(*excludes).get_or_404(source=source)
    return flask.jsonify([tree])


@app.route('/definition/<string:source>')
def route_definition(source):
    excludes = ('id',)
    definition = models.Definition.objects().exclude(*excludes).get_or_404(source=source)
    return flask.jsonify([definition])


# HTTPS proxy for TogoWS
@app.route('/entry/')
@app.route('/entry/<string:entry>')
def route_get_entry(entry=''):
    TOGOWS_GET_ENTRY_ENDPOINT = 'http://togows.org/entry/'
    if re.match(r'^K\d{5}$', entry):
        db = 'kegg-orthology'
    elif re.match(r'^M\d{5}$', entry):
        db = 'kegg-module'
    elif re.match(r'^map\d{5}$', entry):
        db = 'kegg-pathway'
    else:
        flask.abort(404)
    try:
        res = urllib.request.urlopen(TOGOWS_GET_ENTRY_ENDPOINT + db + '/' + entry)
        return flask.Response(res.read(), content_type=res.headers['Content-Type'])
    except urllib.error.HTTPError as e:
        flask.abort(e.code)


@app.route('/action/save_image/', methods=['POST'])
def route_save_image():
    image_format = flask.request.form['format']
    svg = flask.request.form['svg']
    if image_format == 'pdf':
        data = cairosvg.svg2pdf(bytestring=svg)
        mimetype = 'application/pdf'
    elif image_format == 'png':
        data = cairosvg.svg2png(bytestring=svg)
        mimetype = 'image/png'
    elif image_format == 'ps':
        data = cairosvg.svg2ps(bytestring=svg)
        mimetype = 'application/postscript'
    elif image_format == 'svg':
        data = cairosvg.svg2svg(bytestring=svg)
        mimetype = 'image/svg+xml'
    elif image_format == 'raw-svg':
        data = svg
        mimetype = 'image/svg+xml'
    else:
        flask.abort(400)
    return flask.Response(data, mimetype=mimetype)


@app.route('/action/init_profiles/')
@auth.login_required
def route_init_profiles():
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/data/example/profile.json'), 'r')
    input_data = json.load(f)[0]
    models.Profile.objects.all().delete()
    models.Profile(
        profile_id=uuid.uuid4(),
        profile=input_data['profile'],
        series=input_data['series'],
        columns=input_data['columns'],
        target=input_data['target'],
        description=input_data['description'],
        added_at=datetime.datetime.utcnow(),
        expire_at=datetime.datetime(2101, 1, 1),
        private=False,
        locked=True
    ).save()
    return flask.redirect(flask.url_for('route_admin'))


@app.route('/action/update_trees/')
@auth.login_required
def route_update_trees():
    models.Tree.objects.all().delete()
    models.Tree(
        tree=tree.get_tree(),
        source='KEGG',
        description='KEGG version of Functional Tree',
        added_at=datetime.datetime.utcnow()
    ).save()
    cache.clear()
    sources = models.Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    models.Profile.target.choices = models.Definition.source.choices = [source['_id'] for source in sources]
    return flask.redirect(flask.url_for('route_admin'))


@app.route('/action/update_definitions/')
@auth.login_required
def route_update_definitions():
    models.Definition.objects.all().delete()
    models.Definition(
        definition=crckm.get_definition(),
        source='KEGG',
        description='KEGG Module definitions',
        added_at=datetime.datetime.utcnow()
    ).save()
    return flask.redirect(flask.url_for('route_admin'))


@auth.get_password
def auth_get_password(username):
    if username == app.config['FUNCTREE_ADMIN_USERNAME']:
        return app.config['FUNCTREE_ADMIN_PASSWORD']
    return None


@auth.error_handler
def auth_error_handler():
    return flask.render_template('error.html', error=werkzeug.exceptions.Unauthorized()), 401


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(408)
@app.errorhandler(500)
def route_error(error):
    return flask.render_template('error.html', error=error), error.code
