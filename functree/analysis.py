import sys, os, multiprocessing
import numpy as np, pandas as pd
from functree import models

sys.path.append(os.path.join(os.path.dirname(__file__), 'crckm/src'))
import format_and_calculation as crckm


def perform_basic(f, target):
    # Define calculation methods
    methods = ['sum', 'mean']
    # Retrive data from user's input and database
    root = models.Tree.objects().get(source=target)['tree']
    df = pd.read_csv(f, delimiter='\t', comment='#', header=0, index_col=0)
    # Data preparation
    nodes = get_nodes(root)
    # Calculate abundances with multiprocessing
    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    jobs = list()
    for method in methods:
        job = multiprocessing.Process(target=calculate_abundances, args=(df, nodes, method, shared_data), daemon=False)
        job.start()
        jobs.append(job)
    for job in jobs:
        job.join()      # FIXME: Does not work well with Gunicorn
    results = dict(shared_data)
    # Format
    profile = []
    for entry in list(results.values())[0].index:
        values = [results[method].ix[entry].tolist() for method in methods]
        profile.append({
            'entry': entry,
            'values': values
        })
    data = {
        'profile': profile,
        'series': methods,
        'columns': [df.columns.tolist() for i in range(len(methods))]
    }
    return data


def perform_mcr(f, target):
    import copy
    # Retrive data from user's input and database
    root = models.Tree.objects().get(source=target)['tree']
    definition = models.Definition.objects().get(source=target)['definition']
    df = pd.read_csv(f, delimiter='\t', comment='#', header=0, index_col=0)
    # Data preparation
    root = copy.deepcopy(root)
    delete_children(root, 'module')
    nodes = get_nodes(root)
    graph = crckm.format_definition(definition)
    f.seek(0)
    # Calculate MCR
    df_mcr = crckm.calculate(ko_file=f, module_graphs=graph, method='mean', threshold=0)
    # Calculate module/pathway profile
    results = {}
    calculate_abundances(df_mcr, nodes, 'mean', results)
    # Concatenate user's input and results
    df_out = df.applymap(lambda x: int(bool(x))).append(results['mean'])
    # Format
    profile = []
    for entry in df_out.index:
        values = [df_out.ix[entry].tolist()]
        profile.append({
            'entry': entry,
            'values': values
        })
    data = {
        'profile': profile,
        'series': ['MCR'],
        'columns': [df_out.columns.tolist()]
    }
    return data


def calculate_abundances(df, nodes, method, results):
    df_out = pd.DataFrame(columns=df.columns)
    for node in nodes:
        # Skip nodes which was already in df_out or have a name with "*" (e.g. *Module undefined*)
        if node['entry'] in df_out.index or node['entry'].startswith('*'):
            continue
        else:
            # Nodes in the lowest layer (e.g. KO)
            if 'children' not in node:
                try:
                    d = df.loc[node['entry']]
                except KeyError:
                    pass
            # Nodes in internal layer (e.g. Module, Pathway..)
            else:
                targets = [child_node['entry'] for child_node in get_nodes(node) if 'children' not in child_node]
                try:
                    loc = df.loc[targets]
                    d = eval('loc.{}()'.format(method))
                except KeyError:
                    pass
            df_out.ix[node['entry']] = d
    df_out = df_out.fillna(0)
    results[method] = df_out


def get_nodes(node, nodes=None):
    if nodes is None:
        nodes = []
    nodes.append(node)
    if 'children' in node:
        for child_node in node['children']:
            get_nodes(child_node, nodes)
    return nodes


def delete_children(node, layer):
    if node['layer'] == layer:
        node.pop('children')
    if 'children' in node:
        for i in node['children']:
            delete_children(i, layer)
