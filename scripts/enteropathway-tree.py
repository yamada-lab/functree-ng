#!/usr/bin/env python3
import re, copy, argparse, json

def from_tsv():
    
    hierarchy_path = '/home/omixer/Downloads/enteropathway_list.tsv'
    hierarchy_definition_path = '/home/omixer/Downloads/module_table.tsv'
    
    exclude_kos = ['3','5']
    module_kos = {}
    # make a map of module kos
    with open(hierarchy_definition_path, 'rU') as hierarchy_definition_file:
        for line in hierarchy_definition_file:
            tokens = line.split('\t')
            module_kos[tokens[0]] = set(map(lambda x: re.sub(':\d', '', x) , filter(lambda x: x[-1] not in exclude_kos, re.findall('K\d{5}:\d', tokens[-2]))))

    with open(hierarchy_path, 'rU') as hierarchy_file, open('/home/omixer/Downloads/epathway_output.tsv', 'w') as output:
        output.write("L1\tL2\tL3\tL4\tL5\tModule\tKO\n")
        for line in hierarchy_file:
            tokens = line.split('\t')
            levels = '\t'.join(tokens[2:7]) + '\t' + tokens[0] + " " + tokens[1]
            if tokens[0] in module_kos:
                for ko in module_kos[tokens[0]]:
                    output.write(levels + '\t' +  ko + "\n")
            else:
                print(tokens[0] + " is missing")
                
if __name__ == '__main__':
    from_tsv()