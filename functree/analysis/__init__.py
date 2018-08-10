import re
import pandas as pd
from functree import tree, models
from functree.analysis import module_coverage, display, basic_mapping, comparison
from functools import reduce

def map_external_annotations(df):
    '''
    Find KO annotation for the entries of df then create and new df with K Numbers and rows divided by the number of matched KNumbers 
    '''
    
    '''Fetch the annotations in one batch and put in a dict'''
    annotation_map = {}
    kegg_mapping = models.AnnotationMapping.objects(annotation__in=df.index.values.tolist())
    for k_map in kegg_mapping:
        annotation_map[k_map['annotation']] = k_map['ko_map']
    
    '''Prepare a dict for with data annotated based on the mapping'''
    df_dict =  {}
    
    for annotation in df.index:
        #if annotation has a kegg mapping
        if annotation in annotation_map:
            kegg_annotations = annotation_map[annotation]
            # divide by the number of matched kegg annotations to show all KO values
            # On one level up the value will be summed and reflect the original, and thus avoids overcounting
            distributed_abundance = list((df.loc[annotation] / len(kegg_annotations)).to_dict().values())
            for kegg_annotation in kegg_annotations:
                # if KO already in data frame
                if kegg_annotation in df_dict:
                    df_dict[kegg_annotation] = [x+y for x, y in zip(distributed_abundance, df_dict[kegg_annotation])]
                # if first observation of KO
                else:
                    df_dict[kegg_annotation] = distributed_abundance
        else:
            # if no kegg mapping => it is a Knumber or simply unmapped => Append it to the new df
            df_dict[annotation] = list(df.loc[annotation].to_dict().values())
    '''Create a dataframe from the df_dict. Appending to the dataframe on the fly will penalize the performance'''
    df_keggified = pd.DataFrame.from_dict(df_dict, "index")
    df_keggified.columns = df.columns
    
    return df_keggified

def calc_abundances(df, nodes, method, results):
    """
    Generates mean or sum for all levels of functional Tree
    
    FIXME: this is algorithmically sub-optimal as it goes over the tree randomly and also visits all the leaves.
        A better way could be:
            - map the lowest level first seen an unampped list of elements
            - summarize upper layers by matching them from children and then replace if something from the list is matched 
            - repeat till root
    """
    df_dict =  {}
    for node in nodes:
        entry_profile = None
        # Skip nodes which was already in df_out or have a name with "*" (e.g. *Module undefined*)
        if node['entry'] in df_dict or node['entry'].startswith('*'):
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
        # the entry on the tree is not in the submitted profile
        if entry_profile is not None:
            df_dict[node['entry']] = entry_profile.to_dict().values()

    df_out = pd.DataFrame.from_dict(df_dict, "index")
    df_out.columns = df.columns
    df_out = df_out.dropna(how='all').fillna(0.0)
    results[method] = df_out

def calc_distributed_abundances(df, graph, method, results):
    """
    Generates mean or sum for all levels of functional Tree  
    Generate an incidence of KO to parents | layer
    """
    layer_incidence = {}
    result_map = {}

    for entry in list(df.index):
        if entry in graph:
            populate_incidence(graph, entry, entry, 0, layer_incidence)

    for entry in list(df.index):
        if entry in graph:
            # add KO
            result_map[entry] = {entry: df.loc[entry]}
            # nx.DiGraph.reverse(graph)
            populate_abundance(graph, entry, entry, df.loc[entry], result_map, 1, layer_incidence)
    # reduce the result_map and create a df
    df_dict = {}
    for k, v in result_map.items():
        abundance = reduce(lambda x, y: x + y, v.values())
        if method == "mean":
            abundance = abundance / len(v)
        df_dict[k] = abundance.to_dict().values()
    
    df_out = pd.DataFrame.from_dict(df_dict, "index")
    df_out.columns = df.columns
    df_out = df_out.dropna(how='all').fillna(0.0)
    results[method] = df_out
    
def populate_abundance(graph, entry, parent, entry_row, result_map, layerId, layer_incidence):
    parents = graph.predecessors(parent)
    for p in parents:
        # graph-tool is much fater on this 
        #len(set(map(lambda x: x[len(x)-1], list(nx.all_shortest_paths(revG, entry, p)))))
        # weight = 1 Multiplying the weight by the row is to slow below
        abundance = entry_row / layer_incidence[layerId][entry]
        if p in result_map:
            if entry in result_map[p]:
                result_map[p][entry] += abundance 
            else:
                result_map[p][entry] = abundance
        else:
            result_map[p] = {entry: abundance}
        populate_abundance(graph, entry, p, entry_row, result_map, layerId + 1, layer_incidence)

def populate_incidence(graph, entry, parent, layerId, layer_incidence):
    if layerId in layer_incidence:
        if entry in layer_incidence[layerId]:
            layer_incidence[layerId][entry] += 1
        else:
            layer_incidence[layerId][entry] = 1
    else:
        layer_incidence[layerId] = {entry: 1}
    parents = graph.predecessors(parent)
    for p in parents:
        populate_incidence(graph, entry, p, layerId + 1, layer_incidence)

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
