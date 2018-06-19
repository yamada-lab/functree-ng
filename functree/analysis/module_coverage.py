import sys, os, uuid, datetime, copy
import pandas as pd
from functree import app, models, tree, analysis

sys.path.append(os.path.join(os.path.dirname(__file__), '../crckm/src'))
import format_and_calculation as crckm


def from_table(form):
    result = calc_coverages(f=form.input_file.data, target=form.target.data)
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


def calc_coverages(df, target, result_holder, method='mean'):
    """
    Replace this whole part by a call to the GMMs.jar, to reduce the computation time from 2 minutes to None
    """
    root = models.Tree.objects().get(source=target)['tree']
    
    definition = models.Definition.objects().get(source=target)['definition']
    root = copy.deepcopy(root)
    nodes = tree.get_nodes(root)
    entry_to_layer = dict(map(lambda x: (x['entry'], x['layer']), nodes))
    tree.delete_children(root, 'module')
    nodes_no_ko = tree.get_nodes(root)

    ### HACK_START
    graphs = crckm.format_definition(definition)
    
    from tempfile import NamedTemporaryFile
    f = NamedTemporaryFile(delete=False)
    f.close()
    tmp_file = f.name 
    df.to_csv(tmp_file, sep='\t', encoding='utf-8')
    df_crckm = crckm.calculate(ko_file=tmp_file, module_graphs=graphs, method=method, threshold=0)
    os.unlink(tmp_file)
    #tmp_out = "/tmp/out_dir"
    # call
    #kegg_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/data/ortholog_mapping/module_definition_2017_ipath_version')
    #call("java -jar /opt/GMMs/gmms.jar -i %s -o %s -a 2 -c 0 -d %s -e 2 -s average > /dev/null" % (tmp_file, tmp_out, kegg_db), shell=True, env=os.environ.copy())
    # read the coeverage matrix
    #module_coverage = os.path.join(tmp_out, 'modules-coverage.tsv')
    #df_crckm = pd.read_csv(module_coverage, delimiter='\t', comment='#', header=0, index_col=0)
    ### HACK_END 
    
    results = {}
    analysis.calc_abundances(df_crckm, nodes_no_ko, method, results)
 
    # Concatenate user's input and results
    df_out = df.applymap(lambda x: int(bool(x))).append(results[method])
    result_holder["modulecoverage"] = df_out