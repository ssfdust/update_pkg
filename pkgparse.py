import dialog
import argparse
import sys
import re
import textwrap
import pyperclip

def orphans(err, window):
    packages = err.split('Installed orphans:')[1].strip()
    pac_list = [(i, "", True) for i in packages.split()]
    code, tag = window.checklist("Select Packages", choices=pac_list)
    if code == 'ok':
        packages = ' '.join(tag)
        window.clear()
        pyperclip.copy(packages)

def parse_packages(info, window):
    nodes = re.split(pattern='\n([a-zA-Z0-9]+\/.*)\n    ', string=info)
    first = nodes.pop(0)
    nodes = first.split('\n', 1) + nodes
    nodes = iter(nodes)
    choices = []
    for package, desc in zip(nodes, nodes):
        desc = list(filter(None, desc.split('\n')))
        if len(desc) == 1 and len(desc[0]) > 85:
            desc = list(textwrap.wrap(desc[0], width=80 - 4))
        node_c = [(package if c == 0 else "", i.strip(), 0) for c, i in enumerate(desc)]
        choices.extend(node_c)
    code, tag = window.checklist("Select Packages", choices=choices)
    if code == 'ok':
        tag = list(filter(None, tag))
        tag = [re.sub('[a-zA-Z0-9]+\/', repl='', string=ele.split()[0]) for ele in tag]
        window.clear()
        packages = ' '.join(tag)
        pyperclip.copy(packages)

def main(info):
    window = dialog.Dialog(autowidgetsize=True)
    if 'Installed orphans' in info:
        orphans(info, window)
    else:
        parse_packages(info, window)


if sys.stdin:
    data = sys.stdin.read()
else:
    parser = argparse.ArgumentParser()
    parser.add_argument("info")
    args = parser.parse_args()
    data = args.info
main(data)
