#!/usr/bin/env python3
import re, copy, argparse, json

class Node(dict):
    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)

    def add_child(self, node):
        if not 'children' in self:
            self['children'] = list()
        self['children'].append(node)

    def get_nodes(self, nodes=None):
        if nodes is None:
            nodes = []
        nodes.append(self)
        if 'children' in self:
            for i in self['children']:
                i.get_nodes(nodes)
        return nodes

def from_tsv(name, input_path, output_path):
    
    root = Node(entry=name, name=name, layer='root')

    with open(input_path, 'rU') as mapping_file:
        levels = mapping_file.readline().strip().split('\t')
        levels.insert(0, 'root')
        nodes_layer = {key: {} for key in levels}
        nodes_layer['root'] = {'root': root}

        for line in mapping_file:
            entries = line.strip().split('\t')
            # prefix empty cells by parent id
            for index, entry in enumerate(entries):
                if entry == ["", "-"]:
                    unique_entry = levels[index + 1]
                    if index == 0:
                        unique_entry = "root_" + unique_entry
                    else:
                        unique_entry = entries[index - 1] + "_" + unique_entry
                    entries[index] = unique_entry

            for index, entry in enumerate(entries):
                layer = levels[index + 1]
                if entry not in nodes_layer[layer]:
                    parent_layer = levels[index]
                    node = Node(entry=entry, name=entry, layer=layer)
                    if index > 0:
                        nodes_layer[parent_layer][entries[index - 1]].add_child(node)
                    else:
                        nodes_layer[parent_layer]['root'].add_child(node)
                    nodes_layer[layer][entry] = node
    with open(output_path, 'w') as output:
        output.write(json.dumps(root, sort_keys=True, indent=4))

if __name__ == '__main__':
    name = 'Enteropathway Functional Hierarchies'
    #/home/omixer/Downloads/FOAM-onto_rel1.tsv
    ipath ='/home/omixer/Downloads/epathway_output.tsv'
    #/home/omixer/Downloads/FOAM-onto_rel1.json   
    opath = '/home/omixer/Downloads/enteropathway.json'
    from_tsv(name, ipath, opath)