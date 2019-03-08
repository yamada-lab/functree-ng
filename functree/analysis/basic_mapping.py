import uuid, datetime, multiprocessing
import pandas as pd
from functree import app, constants, models, tree, analysis, services

def from_table(form):
    methods=['mean', 'sum']
    if form.modulecoverage.data and services.DefinitionService.has_definition(form.target.data):
        methods.append('modulecoverage')
    result = calc_abundances(f=form.input_file.data, target=form.target.data, methods=methods, distribute=form.distribute.data)
    
    profile_id = constants.NO_MATCHED_HIERARCHIES
    # if rows were mapped 
    if len(result['profile']) > 0:
        colors = []
        if form.color_file.data:
            colors = pd.read_csv(form.color_file.data, header=None, delimiter='\t').as_matrix().tolist()
        utcnow = datetime.datetime.utcnow()
        
        # This inset is 4 seconds
        # Maybe it is document size Or maybe I shoudl use insert instead of save
        profile_id = models.Profile(
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
    
    return profile_id


def calc_abundances(f, target, methods, distribute):
    
    df = analysis.load_input(f)
    # transform external annotations to kegg KOs
    # runs in 1.66
    if target.lower() in ["kegg", "foam", "enteropathway"]:
        df = analysis.map_external_annotations(df)

    # runs in 2 seconds
    # Different querying strategies did not make any difference so far
    root = models.Tree.objects(source=target).only('tree').first()['tree']
    nodes = tree.get_nodes(root)
    entry_to_layer = dict(map(lambda x: (x['entry'], x['layer']), nodes))
    
    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    jobs = list()
    
    # This runs 6 seconds
    for method in methods:
        if not method == "modulecoverage":
            if distribute == True:
                job = multiprocessing.Process(target=analysis.calc_distributed_abundances, args=(df, tree.to_graph(root), method, shared_data), daemon=False)
            else:
                job = multiprocessing.Process(target=analysis.calc_abundances, args=(df, nodes, method, shared_data), daemon=False)
        else:
            job = multiprocessing.Process(target=analysis.module_coverage.calc_coverages, args=(df, target, shared_data), daemon=False)
        job.start()
        jobs.append(job)
    for job in jobs:
        job.join()
    results = dict(shared_data)
    profile = []
    # load KO based entries
    if len(results) > 0:
        entries=list(list(results.values())[0].index)
        if "modulecoverage" in methods:
            entries += list(list(results.values())[2].index)
            entries = list(set(entries))
    
        # This is taking 2 to 4 seconds to run
        for entry in entries:
            #values = [results[method].ix[entry].tolist() for method in methods]
            values = []
            for method in methods:
                if entry in results[method].index:
                    values.append(results[method].ix[entry].tolist())
                else:
                    values.append([0] * df.columns.size)
            profile.append({'entry': entry, 'layer': analysis.get_layer(entry, entry_to_layer), 'values': values})
    data = {
        'profile': profile,
        'series': methods,
        'columns': [df.columns.tolist() for i in range(len(methods))]
    }
    return data
