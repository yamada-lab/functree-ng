import re
import pandas as pd
from functree import tree
from functree.analysis import module_coverage, display, basic_mapping, comparison



def calc_abundances(df, nodes, method, results):
    """
    Generates mean or sum for all levels of functional Tree
    """
    df_out = pd.DataFrame(columns=df.columns)
    for node in nodes:
        entry_profile = None
        # Skip nodes which was already in df_out or have a name with "*" (e.g. *Module undefined*)
        if node['entry'] in df_out.index or node['entry'].startswith('*'):
            continue

        if 'children' not in node:
            try:
                # If node in abundace matrix, input as is
                entry_profile = df.loc[node['entry']]
            except KeyError:
                pass
        else:
            # filter out module unknown nodes
            targets = [child_node['entry'] for child_node in tree.get_nodes(node) if 'children' not in child_node and not child_node['entry'].startswith('*')]
            try:
                # loc is row names of data frame
                loc = df.loc[targets]
                # sample abundance for a biological entry
                # Calculated for children of nodes that are not in the input abundance matrix
                entry_profile = eval('loc.{}()'.format(method))
            except KeyError:
                pass
        df_out.ix[node['entry']] = entry_profile

    df_out = df_out.dropna(how='all').fillna(0.0)
    results[method] = df_out


def get_layer(entry, entry_to_layer):
    try:
        layer = entry_to_layer[entry]
    except KeyError:
        if re.match(r'^K\d{5}$', entry):
            layer = 'ko'
        elif re.match(r'^M\d{5}$', entry):
            layer = 'module'
        elif re.match(r'^map\d{5}$', entry):
            layer = 'pathway'
        else:
            layer = None
    return layer
