import datetime, json, os, uuid, urllib.request, urllib.error, re
import flask, werkzeug.exceptions, cairosvg
import mimetypes
from flask import jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
from functree import __version__, app, auth, csrf, filters, forms, models, tree, analysis, cache
from functree.crckm.src import download as crckm

@app.route('/')
def route_index():
    return flask.render_template('index.html')

@app.route('/api/mapping/', methods=['POST'])
@csrf.exempt
def mapping():
    form = forms.MappingForm(csrf_enabled=False)
    if form.validate_on_submit():
        profile_id = analysis.basic_mapping.from_table(form)
        return jsonify({'profile_id': profile_id})
    else:
        return jsonify({'errors': form.errors})

@app.route('/api/comparison/', methods=['POST'])
@csrf.exempt
def comparison():
    form = forms.MappingForm(csrf_enabled=False)
    if form.validate_on_submit():
        profile_id = analysis.basic_mapping.from_table(form)
        return jsonify({'profile_id': profile_id})
    else:
        return jsonify({'errors': form.errors})

@app.route('/api/display/', methods=['POST'])
@csrf.exempt
def api_display():
    form = forms.DisplayForm(csrf_enabled=False)
    if form.validate_on_submit():
        profile_id = profile_for_display(form)
        return jsonify({'profile_id': profile_id})
    else:
        return jsonify({'errors': form.errors})

@app.route('/api/viewer/', methods=['GET'])
def api_viewer():
    # process args 
    profile_id = request.args.get('profile_id', type=uuid.UUID)
    series_value = request.args.get('series')
    column_values = request.args.get("columns").split(",")
    circle_column_value = request.args.get("circle-column")
    is_stack = request.args.get("stack")
    is_disable_normalization = request.args.get("disable-normalization")
    color_code=request.args.get("color-code")
    depth_value=request.args.get("depth")
    # initialize a headless chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--auto-open-devtools-for-tabs')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("window-size=1980,1200");
    svg = None
    driver = None
    try:
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # locate the page
        page=flask.url_for('route_viewer', _external=True) + '?profile_id={}'.format(profile_id)
        browser = driver.get(page)
        wait = WebDriverWait(driver, 60)
        # Wait for page to load
        wait.until(EC.invisibility_of_element_located((By.ID, 'loading')))
        # open the options
        options = driver.find_element_by_id("options").click()
        driver.implicitly_wait(0.5)
        # select a series to visualize
        series = Select(driver.find_element_by_id("series"))
        series.select_by_visible_text(series_value)
        driver.implicitly_wait(0.5)
        # select samples
        columns = Select(driver.find_element_by_id("columns"))
        for column in column_values:
            columns.select_by_visible_text(column)
        if circle_column_value:
            circle_map = Select(driver.find_element_by_id("circle-map"))
            circle_map.select_by_visible_text(circle_column_value)
        
        driver.implicitly_wait(0.5)
        if is_stack == "":
            driver.find_element_by_id("stacking").click()
        if is_disable_normalization == "":
            driver.find_element_by_id("normalize").click()
        if color_code:
            color_coding = Select(driver.find_element_by_id("color-coding"))
            color_coding.select_by_visible_text(color_code)
        if depth_value:
            depth = Select(driver.find_element_by_id("depth"))
            depth.select_by_visible_text(depth_value)
        # update
        driver.find_element_by_id("update").click()
        # Giuve a couple of seconds to let the SVG update 
        driver.implicitly_wait(2)
        # locate the svg element
        svgEl = driver.find_element_by_tag_name("svg")
        # copy it
        svg = svgEl.get_attribute('outerHTML')
    finally:
        driver.quit()
    # return the raw SVG file
    return str(svg)

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
            return flask.render_template('comparison.html', form=form, mode=mode)
    elif mode == 'display':
        form = forms.DisplayForm()
        if form.validate_on_submit():
            profile_id = profile_for_display(form)
            if not profile_id:
                # TODO add error message | or hadnle this at validation with custom validators
                return flask.render_template('display.html', form=form, mode=mode)
            return flask.redirect(flask.url_for('route_viewer') + '?profile_id={}'.format(profile_id))
        else:
            return flask.render_template('display.html', form=form, mode=mode)
    else:
        flask.abort(404)

def profile_for_display(form):
    profile_id = None
    file_type = mimetypes.MimeTypes().guess_type(form.input_file.data.filename)[0]
    if file_type == "application/json":
        profile_id = analysis.display.from_json(form)
    elif file_type == 'text/tab-separated-values':
        profile_id = analysis.display.from_table(form)
    return profile_id

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

@app.route('/data/upload/', methods=['GET', 'POST'])
def route_data_upload():
    form = forms.UploadForm()
    if form.validate_on_submit():
        models.Tree(
            tree=tree.from_json(form.input_file.data),
            source=form.target.data,
            description=form.description.data,
            added_at=datetime.datetime.utcnow()).save()
        cache.clear()
        return flask.redirect(flask.url_for('route_data'))
    else:
        return flask.render_template('upload.html', form=form)    

@app.context_processor
def utility_processor():
    def json_schema():
        schema = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/data/example/data-schema.json'), 'r')
        return schema.read()
    def json_example():
        data = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/data/example/data-example.json'), 'r')
        return data.read()
    return dict(json_schema=json_schema, json_example=json_example)

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
        description='KEGG BRITE Functional Hierarchies',
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

@app.route('/action/update_annotation_mapping/')
@auth.login_required
def route_update_annotation_mapping():
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/data/ortholog_mapping/external_annotation.map')
    orto_mapping = {}
    with open(f, 'rU') as mapping_file:
        for line in mapping_file:
            tokens = line.rstrip().split('\t', 1)
            if tokens[0] not in orto_mapping:
                orto_mapping[tokens[0]] = set()
            orto_mapping[tokens[0]].add(tokens[1])
    # drop current collection
    models.AnnotationMapping.drop_collection()
    # upload in batches
    batch = []
    target_size = 5000
    for x in orto_mapping:
        batch.append(models.AnnotationMapping(
            annotation=x,
            ko_map=orto_mapping[x]
        ))
        if len(batch) == target_size:
            models.AnnotationMapping.objects.insert(batch, load_bulk=False, signal_kwargs={'ordered': False} )
            batch.clear()
    # insert the remaning annotations
    models.AnnotationMapping.objects.insert(batch, load_bulk=False, signal_kwargs={'ordered': False} )
    models.AnnotationMapping.create_index('annotation')

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
