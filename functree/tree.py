#!/usr/bin/env python3
import re, copy, urllib.request, urllib.parse, argparse, json

KEGG_DOWNLOAD_HTEXT_ENDPOINT = 'http://www.genome.jp/kegg-bin/download_htext?'
EXCLUDES = ['Global and overview maps', 'Drug Development', 'Chemical structure transformation maps']


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


def get_tree():
    nodes_layer = {key: [] for key in ['brite0', 'brite1', 'brite2', 'pathway', 'module', 'ko']}
    root = Node(entry='KEGG BRITE Functional Hierarchies', name='KEGG BRITE Functional Hierarchies', layer='brite0')
    nodes_layer['brite0'].append(root)

    with download_htext(htext='br08901.keg') as f:
        for line in f.read().decode('utf-8').split('\n'):
            if line.startswith('A'):
                layer = 'brite1'
                line = line.lstrip('A').lstrip()
                entry = name = re.sub(r'<[^>]*?>', '', line)
                node = Node(entry=entry, name=name, layer=layer)
                nodes_layer['brite0'][-1].add_child(node)
                nodes_layer[layer].append(node)
                continue
            if line.startswith('B'):
                layer = 'brite2'
                line = line.lstrip('B').lstrip()
                entry = name = line
                node = Node(entry=entry, name=name, layer=layer)
                nodes_layer['brite1'][-1].add_child(node)
                nodes_layer[layer].append(node)
                continue
            if line.startswith('C'):
                layer = 'pathway'
                line = line.lstrip('C').lstrip()
                entry, name = line.split(maxsplit=1)
                entry = 'map{}'.format(entry)
                node = Node(entry=entry, name=name, layer=layer)
                nodes_layer['brite2'][-1].add_child(node)
                nodes_layer[layer].append(node)

    with download_htext(htext='ko00002.keg') as f:
        for line in f.read().decode('utf-8').split('\n'):
            if line.startswith('D'):
                layer = 'module'
                line = line.lstrip('D').lstrip()
                entry, name = line.split(maxsplit=1)
                node = Node(entry=entry, name=name, layer=layer)
                nodes_layer[layer].append(node)
                continue
            if line.startswith('E'):
                layer = 'ko'
                line = line.lstrip('E').lstrip()
                entry, name = line.split(maxsplit=1)
                node = Node(entry=entry, name=name, layer=layer)
                nodes_layer['module'][-1].add_child(node)

    # Link modules to all associated pathways
    nodes = root.get_nodes()
    for node in nodes_layer['module']:
        parents_match = re.search(r'\[.+?\]', node['name'])
        if parents_match:
            parent_entries_ = parents_match.group()[1:-1].lstrip('PATH:').split()
            parent_entries = filter(lambda x: re.match('map', x), parent_entries_)
            for parent_entry in parent_entries:
                targets = filter(lambda x: x['entry'] == parent_entry, nodes)
                for target in targets:
                    target.add_child(copy.deepcopy(node))

    # Add KOs which belong to not module but pathway
    nodes = root.get_nodes()
    with download_htext(htext='ko00001.keg') as f:
        for line in f.read().decode('utf-8').split('\n'):
            if line.startswith('C'):
                line = line.lstrip('C').lstrip()
                entry = line.split(maxsplit=1)[0]
                entry = 'map{}'.format(entry)
                targets = list(filter(lambda x: x['entry'] == entry, nodes))
                continue
            if line.startswith('D'):
                layer = 'ko'
                line = line.lstrip('D').lstrip()
                entry, name = line.split(maxsplit=1)
                for target in targets:
                    child_ko_entries = map(lambda x: x['entry'], filter(lambda x: x['layer'] == 'ko', target.get_nodes()))
                    if not entry in child_ko_entries:
                        if 'children' not in target:
                            node = Node(entry='*Module undefined*', name='*Module undefined*', layer='module')
                            target.add_child(node)
                        elif target['children'][-1]['entry'] != '*Module undefined*':
                            node = Node(entry='*Module undefined*', name='*Module undefined*', layer='module')
                            target.add_child(node)
                        node = Node(entry=entry, name=name, layer=layer)
                        target['children'][-1].add_child(node)

    # Remove nodes which are listed on EXCLUDES
    for node in filter(lambda x: x['layer'] != 'ko', root.get_nodes()):
        if 'children' in node:
            for child_node in node['children'][:]:
                if child_node['entry'] in EXCLUDES:
                    node['children'].remove(child_node)
    # Remove nodes which do not have children
    for node in filter(lambda x: x['layer'] not in ['ko', 'module'], root.get_nodes()):
        if 'children' in node:
            for child_node in node['children'][:]:
                if 'children' not in child_node:
                    node['children'].remove(child_node)
    return root


def from_json(path):
    root = json.load(path)
    return root

def from_tsv(path, name):
    '''
    Turns a TSV formatted hierarchy into a JSON-like, FuncTree compatible hierarchy
    '''
    root = Node(entry=name, name=name, layer='root')

    with open(path, 'rU') as mapping_file:
        levels = mapping_file.readline().strip().split('\t')
        levels.insert(0, 'root')
        nodes_layer = {key: {} for key in levels}
        nodes_layer['root'] = {'root': root}

        for line in mapping_file:
            entries = line.strip().split('\t')
            # prefix empty cells by parent id
            for index, entry in enumerate(entries):
                if entry == "":
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
    return root

def download_htext(htext, format='htext'):
    params = {
        'htext': htext,
        'format': format
    }
    url = KEGG_DOWNLOAD_HTEXT_ENDPOINT + urllib.parse.urlencode(params)
    res = urllib.request.urlopen(url)
    return res


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


def parse_arguments():
    parser = argparse.ArgumentParser(prog=__file__, description='Functional Tree JSON generator')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.2.0')
    parser.add_argument('-o', '--output', metavar='file', type=argparse.FileType('w'), default=sys.stdout, help='write output to file')
    parser.add_argument('-i', '--indent', metavar='level', type=int, default=None, help='specify indent level')
    return parser.parse_args()


if __name__ == '__main__':
    import sys, json, datetime
    args = parse_arguments()
    data = {
        'tree': get_tree(),
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    args.output.write(json.dumps(data, indent=args.indent) + '\n')
